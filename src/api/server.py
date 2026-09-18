import json
import os
import sys
import uuid
from urllib.parse import quote

import requests
from flask import Flask, jsonify, request, send_from_directory


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from persistence_helper import load_ledger, load_observations, save_ledger, save_observations
from src.core.economics import Allocation, AssetCreatedEvent, RevenueEvent, calculate_allocations, calculate_balances, validate_allocations
from src.core.observation import Observation
from src.api.comics import comics_api, answer_catalog


app = Flask(__name__)
app.register_blueprint(comics_api)

OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://host.docker.internal:11434").rstrip("/")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "mistral:latest")
OLLAMA_EMBEDDING_MODEL = os.environ.get("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
QDRANT_URL = os.environ.get("QDRANT_URL", "http://qdrant:6333").rstrip("/")
QDRANT_COLLECTION = os.environ.get("QDRANT_COLLECTION", "myzubster")
AI_REQUEST_TIMEOUT = float(os.environ.get("AI_REQUEST_TIMEOUT", "120"))
AI_CONTEXT_LIMIT = int(os.environ.get("AI_CONTEXT_LIMIT", "5"))
AI_MAX_QUESTION_LENGTH = int(os.environ.get("AI_MAX_QUESTION_LENGTH", "2000"))


@app.route("/", methods=["GET"])
def landing_page():
    return send_from_directory(PROJECT_ROOT, "index.html")


def _request_json(method, url, **kwargs):
    response = requests.request(method, url, timeout=AI_REQUEST_TIMEOUT, **kwargs)
    response.raise_for_status()
    if not response.content:
        return {}
    return response.json()


def _ollama_embedding(text):
    payload = _request_json(
        "POST",
        f"{OLLAMA_BASE_URL}/api/embed",
        json={"model": OLLAMA_EMBEDDING_MODEL, "input": text},
    )
    embeddings = payload.get("embeddings")
    if not isinstance(embeddings, list) or not embeddings or not embeddings[0]:
        raise ValueError("Ollama non ha restituito un embedding valido")
    return embeddings[0]


def _ensure_qdrant_collection(vector_size):
    collection_url = f"{QDRANT_URL}/collections/{quote(QDRANT_COLLECTION, safe='')}"
    response = requests.get(collection_url, timeout=AI_REQUEST_TIMEOUT)
    if response.status_code == 404:
        _request_json(
            "PUT",
            collection_url,
            json={"vectors": {"size": vector_size, "distance": "Cosine"}},
        )
        return
    response.raise_for_status()


def _index_observations(observations):
    if not observations:
        return 0

    points = []
    for index, observation in enumerate(observations):
        description = str(observation.get("description", "")).strip()
        if not description:
            continue

        vector = _ollama_embedding(description)
        _ensure_qdrant_collection(len(vector))

        point_id = observation.get("id") or index
        if isinstance(point_id, str):
            try:
                point_id = int(point_id, 16)
            except ValueError:
                point_id = index

        points.append(
            {
                "id": point_id,
                "vector": vector,
                "payload": {"observation": observation},
            }
        )

    if not points:
        return 0

    collection = quote(QDRANT_COLLECTION, safe="")
    _request_json(
        "PUT",
        f"{QDRANT_URL}/collections/{collection}/points?wait=true",
        json={"points": points},
    )
    return len(points)


def _search_observations(question):
    question_vector = _ollama_embedding(question)
    _ensure_qdrant_collection(len(question_vector))

    collection = quote(QDRANT_COLLECTION, safe="")
    result = _request_json(
        "POST",
        f"{QDRANT_URL}/collections/{collection}/points/query",
        json={
            "query": question_vector,
            "limit": AI_CONTEXT_LIMIT,
            "with_payload": True,
        },
    )

    matches = result.get("result", {}).get("points", [])
    return [
        match.get("payload", {}).get("observation")
        for match in matches
        if match.get("payload", {}).get("observation")
    ]


def _generate_answer(question, context):
    context_text = "\n".join(
        (
            f"[FONTE {index}] "
            f"description={observation.get('description', '')}\n"
            f"metadata={json.dumps(observation.get('metadata', {}), ensure_ascii=False, sort_keys=True)}"
        )
        for index, observation in enumerate(context, start=1)
    )
    if not context_text:
        context_text = "NESSUNA FONTE DISPONIBILE"

    payload = _request_json(
        "POST",
        f"{OLLAMA_BASE_URL}/api/chat",
        json={
            "model": OLLAMA_MODEL,
            "stream": False,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Sei l'assistente evidence-first di MyZubster. "
                        "Usa esclusivamente fatti esplicitamente presenti nelle FONTI. "
                        "Non inventare e non dedurre informazioni mancanti. "
                        "Ignora le fonti non pertinenti. "
                        "Se la risposta non e presente nelle fonti, rispondi esattamente: "
                        "'Informazione non disponibile nelle fonti MyZubster.' "
                        "Rispondi in italiano in modo breve e fattuale."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"FONTI:\n{context_text}\n\n"
                        f"DOMANDA:\n{question}\n\n"
                        "Estrai soltanto i fatti necessari per rispondere."
                    ),
                },
            ],
        },
    )
    answer = payload.get("message", {}).get("content")
    if not isinstance(answer, str) or not answer.strip():
        raise ValueError("Ollama non ha restituito una risposta valida")
    return answer.strip()


@app.route("/api/observation", methods=["POST"])
def create_observation():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Corpo JSON obbligatorio"}), 400

    description = data.get("description")
    if not isinstance(description, str) or not description.strip():
        return jsonify({"error": "Descrizione obbligatoria"}), 400

    try:
        latitude = float(data.get("latitude", 0))
        longitude = float(data.get("longitude", 0))
    except (TypeError, ValueError):
        return jsonify({"error": "Coordinate non valide"}), 400

    if not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
        return jsonify({"error": "Coordinate fuori intervallo"}), 400

    observation = Observation(
        description=description.strip(),
        latitude=latitude,
        longitude=longitude,
        media_hash=str(data.get("media_hash", "")),
    ).to_dict()

    metadata = data.get("metadata")
    if metadata is not None:
        if not isinstance(metadata, dict):
            return jsonify({"error": "Metadata non validi"}), 400
        observation["metadata"] = metadata

    try:
        observations = load_observations()
        observations.append(observation)
        save_observations(observations)
    except (OSError, ValueError) as error:
        app.logger.exception("Impossibile salvare l'osservazione")
        return jsonify({"error": f"Persistenza non disponibile: {error}"}), 500

    try:
        _index_observations([observation])
    except (OSError, ValueError, requests.RequestException) as error:
        app.logger.exception(
            "Osservazione salvata ma indicizzazione AI non disponibile: %s",
            error,
        )

    return jsonify(observation), 201


@app.route("/api/observations", methods=["GET"])
def list_observations():
    try:
        observations = load_observations()
    except (OSError, ValueError) as error:
        app.logger.exception("Impossibile leggere le osservazioni")
        return jsonify({"error": f"Persistenza non disponibile: {error}"}), 500
    return jsonify({"count": len(observations), "observations": observations})



@app.route("/api/ledger/revenue", methods=["POST"])
def create_revenue_event():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Corpo JSON obbligatorio"}), 400

    try:
        amount = float(data["amount"])
        currency = str(data["currency"]).strip()
        source = str(data["source"]).strip()
        allocations_data = data["allocations"]
    except (KeyError, TypeError, ValueError):
        return jsonify({"error": "source, amount, currency e allocations sono obbligatori"}), 400

    if not source or not currency or amount < 0 or not isinstance(allocations_data, list):
        return jsonify({"error": "Dati revenue non validi"}), 400

    try:
        allocations = tuple(
            Allocation(
                participant_id=str(item["participant_id"]).strip(),
                percentage=float(item["percentage"]),
            )
            for item in allocations_data
        )
        validate_allocations(allocations)
        amounts = calculate_allocations(amount, allocations)
    except (KeyError, TypeError, ValueError) as error:
        return jsonify({"error": f"Allocazioni non valide: {error}"}), 400

    event = RevenueEvent(
        event_id=str(data.get("event_id") or uuid.uuid4()),
        source=source,
        amount=amount,
        currency=currency,
        allocations=allocations,
        status=str(data.get("status") or "RECORDED"),
    )
    record = event.to_dict()
    record["calculated_amounts"] = amounts

    try:
        ledger = load_ledger()
        if any(item.get("event_id") == record["event_id"] for item in ledger):
            return jsonify({"error": "event_id già presente nel ledger"}), 409
        ledger.append(record)
        save_ledger(ledger)
    except (OSError, ValueError) as error:
        app.logger.exception("Impossibile salvare il revenue event")
        return jsonify({"error": f"Ledger non disponibile: {error}"}), 500

    return jsonify(record), 201


@app.route("/api/ledger/assets", methods=["POST"])
def create_asset_event():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Corpo JSON obbligatorio"}), 400

    asset_id = data.get("asset_id")
    asset_type = data.get("asset_type")
    creator_id = data.get("creator_id")
    if not all(isinstance(value, str) and value.strip() for value in (asset_id, asset_type, creator_id)):
        return jsonify({"error": "asset_id, asset_type e creator_id sono obbligatori"}), 400

    event = AssetCreatedEvent(
        event_id=str(data.get("event_id") or uuid.uuid4()),
        asset_id=asset_id.strip(),
        asset_type=asset_type.strip(),
        creator_id=creator_id.strip(),
        provenance_status=str(data.get("provenance_status") or "RECORDED"),
    )
    record = event.to_dict()

    try:
        ledger = load_ledger()
        if any(item.get("event_id") == record["event_id"] for item in ledger):
            return jsonify({"error": "event_id già presente nel ledger"}), 409
        ledger.append(record)
        save_ledger(ledger)
    except (OSError, ValueError) as error:
        app.logger.exception("Impossibile salvare l'asset event")
        return jsonify({"error": f"Ledger non disponibile: {error}"}), 500

    return jsonify(record), 201


@app.route("/api/ledger/revenue", methods=["GET"])
def list_revenue_events():
    try:
        events = [
            event for event in load_ledger()
            if event.get("event_type") == "REVENUE"
        ]
    except (OSError, ValueError) as error:
        app.logger.exception("Impossibile leggere il revenue ledger")
        return jsonify({"error": f"Ledger non disponibile: {error}"}), 500
    return jsonify({"count": len(events), "events": events})


@app.route("/api/ledger/assets", methods=["GET"])
def list_asset_events():
    try:
        events = [
            event for event in load_ledger()
            if event.get("event_type") == "ASSET_CREATED"
        ]
    except (OSError, ValueError) as error:
        app.logger.exception("Impossibile leggere gli asset ledger")
        return jsonify({"error": f"Ledger non disponibile: {error}"}), 500
    return jsonify({"count": len(events), "events": events})


@app.route("/api/ledger/balances", methods=["GET"])
def list_ledger_balances():
    try:
        balances = calculate_balances(load_ledger())
    except (OSError, ValueError, TypeError) as error:
        app.logger.exception("Impossibile calcolare i balance")
        return jsonify({"error": f"Ledger non disponibile: {error}"}), 500

    participants = [
        {
            "participant_id": participant_id,
            "balances": currencies,
        }
        for participant_id, currencies in sorted(balances.items())
    ]
    return jsonify({"participants": participants})


@app.route("/api/ledger", methods=["GET"])
def list_ledger():
    try:
        events = load_ledger()
    except (OSError, ValueError) as error:
        app.logger.exception("Impossibile leggere il ledger")
        return jsonify({"error": f"Ledger non disponibile: {error}"}), 500
    return jsonify({"count": len(events), "events": events})


def _authoritative_metadata_answer(question, context):
    if not context:
        return None

    metadata = context[0].get("metadata")
    if not isinstance(metadata, dict):
        return None

    question_lower = question.lower()
    parts = []

    if "status" in metadata and any(
        term in question_lower
        for term in ("stato", "status")
    ):
        parts.append(f"Stato: {metadata['status']}.")

    if "onchainRecorded" in metadata and any(
        term in question_lower
        for term in ("blockchain", "onchain", "on-chain")
    ):
        value = metadata["onchainRecorded"]
        if isinstance(value, bool):
            parts.append(
                "Registrazione blockchain: "
                + ("SI." if value else "no.")
            )

    if "paymentRequired" in metadata and any(
        term in question_lower
        for term in ("pagamento", "payment")
    ):
        value = metadata["paymentRequired"]
        if isinstance(value, bool):
            parts.append(
                "Pagamento richiesto: "
                + ("SI." if value else "no.")
            )

    if "success" in metadata and any(
        term in question_lower
        for term in ("successo", "success", "riuscito")
    ):
        value = metadata["success"]
        if isinstance(value, bool):
            parts.append(
                "Operazione riuscita: "
                + ("SI." if value else "no.")
            )

    return " ".join(parts) if parts else None

@app.route("/api/ai/ask", methods=["POST"])
def ask_ai():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Corpo JSON obbligatorio"}), 400

    if data.get("topic") == "nicola-comics":
        return answer_catalog(data)

    question = data.get("question")
    if not isinstance(question, str) or not question.strip():
        return jsonify({"error": "Domanda obbligatoria"}), 400

    question = question.strip()
    if len(question) > AI_MAX_QUESTION_LENGTH:
        return jsonify({"error": "Domanda troppo lunga"}), 400

    try:
        context = _search_observations(question)
        answer = _authoritative_metadata_answer(question, context)
        if answer is None:
            answer = _generate_answer(question, context)
    except (OSError, ValueError) as error:
        app.logger.exception("Errore durante la richiesta AI")
        return jsonify({"error": f"Risposta AI non disponibile: {error}"}), 502
    except requests.RequestException:
        app.logger.exception("Ollama o Qdrant non raggiungibile")
        return jsonify({"error": "Servizio AI temporaneamente non disponibile"}), 503

    return jsonify(
        {
            "answer": answer,
            "model": OLLAMA_MODEL,
            "embedding_model": OLLAMA_EMBEDDING_MODEL,
            "sources": context,
        }
    )


if __name__ == "__main__":
    app.run(
        host=os.environ.get("MYZUBSTER_HOST", "127.0.0.1"),
        port=int(os.environ.get("MYZUBSTER_PORT", "5000")),
        debug=False,
    )
