import json
import os
import sys
import uuid
from urllib.parse import quote

import requests
from flask import Flask, jsonify, request, send_from_directory


PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, PROJECT_ROOT)

from persistence_helper import (
    load_ledger,
    load_observations,
    save_ledger,
    save_observations,
)
from src.core.economics import (
    Allocation,
    AssetCreatedEvent,
    RevenueEvent,
    calculate_allocations,
    calculate_balance_breakdown,
    normalize_revenue_source,
    simulate_revenue,
    validate_allocations,
)
from src.core.observation import Observation
from src.core.knowledge_proof import verify_knowledge_proof
from src.api.comics import comics_api, answer_catalog


app = Flask(__name__)
app.register_blueprint(comics_api)

OLLAMA_BASE_URL = os.environ.get(
    "OLLAMA_BASE_URL",
    "http://host.docker.internal:11434",
).rstrip("/")

OLLAMA_MODEL = os.environ.get(
    "OLLAMA_MODEL",
    "mistral:latest",
)

OLLAMA_EMBEDDING_MODEL = os.environ.get(
    "OLLAMA_EMBEDDING_MODEL",
    "nomic-embed-text",
)

QDRANT_URL = os.environ.get(
    "QDRANT_URL",
    "http://qdrant:6333",
).rstrip("/")

QDRANT_COLLECTION = os.environ.get(
    "QDRANT_COLLECTION",
    "myzubster",
)

AI_REQUEST_TIMEOUT = float(
    os.environ.get("AI_REQUEST_TIMEOUT", "120")
)

AI_CONTEXT_LIMIT = int(
    os.environ.get("AI_CONTEXT_LIMIT", "5")
)

AI_MAX_QUESTION_LENGTH = int(
    os.environ.get("AI_MAX_QUESTION_LENGTH", "2000")
)


@app.route("/", methods=["GET"])
def landing_page():
    return send_from_directory(
        PROJECT_ROOT,
        "index.html",
    )


def _request_json(method, url, **kwargs):
    response = requests.request(
        method,
        url,
        timeout=AI_REQUEST_TIMEOUT,
        **kwargs,
    )
    response.raise_for_status()

    if not response.content:
        return {}

    return response.json()


def _ollama_embedding(text):
    payload = _request_json(
        "POST",
        f"{OLLAMA_BASE_URL}/api/embed",
        json={
            "model": OLLAMA_EMBEDDING_MODEL,
            "input": text,
        },
    )

    embeddings = payload.get("embeddings")

    if (
        not isinstance(embeddings, list)
        or not embeddings
        or not embeddings[0]
    ):
        raise ValueError(
            "Ollama non ha restituito un embedding valido"
        )

    return embeddings[0]


def _ensure_qdrant_collection(vector_size):
    collection_url = (
        f"{QDRANT_URL}/collections/"
        f"{quote(QDRANT_COLLECTION, safe='')}"
    )

    response = requests.get(
        collection_url,
        timeout=AI_REQUEST_TIMEOUT,
    )

    if response.status_code == 404:
        _request_json(
            "PUT",
            collection_url,
            json={
                "vectors": {
                    "size": vector_size,
                    "distance": "Cosine",
                }
            },
        )
        return

    response.raise_for_status()


def _index_observations(observations):
    if not observations:
        return 0

    points = []

    for index, observation in enumerate(observations):
        description = str(
            observation.get("description", "")
        ).strip()

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
                "payload": {
                    "observation": observation,
                },
            }
        )

    if not points:
        return 0

    collection = quote(
        QDRANT_COLLECTION,
        safe="",
    )

    _request_json(
        "PUT",
        (
            f"{QDRANT_URL}/collections/"
            f"{collection}/points?wait=true"
        ),
        json={
            "points": points,
        },
    )

    return len(points)


def _reindex_observations():
    observations = load_observations()
    return _index_observations(observations)


def _find_observation_by_id_in_question(question):
    candidates = {
        token.strip(".,;:!?()[]{}\"'")
        for token in question.split()
    }

    observation_ids = {
        candidate
        for candidate in candidates
        if len(candidate) == 16
        and all(
            character in "0123456789abcdefABCDEF"
            for character in candidate
        )
    }

    if not observation_ids:
        return None

    for observation in load_observations():
        if observation.get("id") in observation_ids:
            return observation

    return None


def _search_observations(question):
    exact_observation = _find_observation_by_id_in_question(
        question
    )

    if exact_observation is not None:
        return [exact_observation]

    question_vector = _ollama_embedding(question)
    _ensure_qdrant_collection(
        len(question_vector)
    )

    collection = quote(
        QDRANT_COLLECTION,
        safe="",
    )

    result = _request_json(
        "POST",
        (
            f"{QDRANT_URL}/collections/"
            f"{collection}/points/query"
        ),
        json={
            "query": question_vector,
            "limit": AI_CONTEXT_LIMIT,
            "with_payload": True,
        },
    )

    matches = result.get(
        "result",
        {},
    ).get(
        "points",
        [],
    )

    return [
        match.get(
            "payload",
            {},
        ).get("observation")
        for match in matches
        if match.get(
            "payload",
            {},
        ).get("observation")
    ]


def _generate_answer(question, context):
    context_parts = []

    for index, observation in enumerate(
        context,
        start=1,
    ):
        description = observation.get(
            "description",
            "",
        )

        metadata = json.dumps(
            observation.get(
                "metadata",
                {},
            ),
            ensure_ascii=False,
            sort_keys=True,
        )

        context_parts.append(
            (
                f"[FONTE {index}] "
                f"description={description}\n"
                f"metadata={metadata}"
            )
        )

    context_text = "\n".join(
        context_parts
    )

    if not context_text:
        context_text = (
            "NESSUNA FONTE DISPONIBILE"
        )

    payload = _request_json(
        "POST",
        f"{OLLAMA_BASE_URL}/api/chat",
        json={
            "model": OLLAMA_MODEL,
            "stream": False,
            "keep_alive": "10m",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Sei l'assistente evidence-first "
                        "di MyZubster. "
                        "Usa esclusivamente fatti "
                        "esplicitamente presenti nelle FONTI. "
                        "Non inventare e non dedurre "
                        "informazioni mancanti. "
                        "Ignora le fonti non pertinenti. "
                        "Se la risposta non e presente "
                        "nelle fonti, rispondi esattamente: "
                        "'Informazione non disponibile "
                        "nelle fonti MyZubster.' "
                        "Rispondi in italiano in modo "
                        "breve e fattuale."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"FONTI:\n{context_text}\n\n"
                        f"DOMANDA:\n{question}\n\n"
                        "Estrai soltanto i fatti necessari "
                        "per rispondere."
                    ),
                },
            ],
        },
    )

    answer = payload.get(
        "message",
        {},
    ).get("content")

    if (
        not isinstance(answer, str)
        or not answer.strip()
    ):
        raise ValueError(
            "Ollama non ha restituito "
            "una risposta valida"
        )

    return answer.strip()


@app.route(
    "/api/observation",
    methods=["POST"],
)
def create_observation():
    data = request.get_json(
        silent=True
    )

    if not isinstance(data, dict):
        return jsonify(
            {
                "error": (
                    "Corpo JSON obbligatorio"
                )
            }
        ), 400

    description = data.get(
        "description"
    )

    if (
        not isinstance(description, str)
        or not description.strip()
    ):
        return jsonify(
            {
                "error": (
                    "Descrizione obbligatoria"
                )
            }
        ), 400

    try:
        latitude = float(
            data.get("latitude", 0)
        )
        longitude = float(
            data.get("longitude", 0)
        )
    except (TypeError, ValueError):
        return jsonify(
            {
                "error": (
                    "Coordinate non valide"
                )
            }
        ), 400

    if (
        not -90 <= latitude <= 90
        or not -180 <= longitude <= 180
    ):
        return jsonify(
            {
                "error": (
                    "Coordinate fuori intervallo"
                )
            }
        ), 400

    observation = Observation(
        description=description.strip(),
        latitude=latitude,
        longitude=longitude,
        media_hash=str(
            data.get("media_hash", "")
        ),
    ).to_dict()

    metadata = data.get("metadata")

    if metadata is not None:
        if not isinstance(metadata, dict):
            return jsonify(
                {
                    "error": (
                        "Metadata non validi"
                    )
                }
            ), 400

        observation["metadata"] = metadata

    try:
        observations = load_observations()
        observations.append(observation)
        save_observations(observations)

    except (OSError, ValueError) as error:
        app.logger.exception(
            "Impossibile salvare "
            "l'osservazione"
        )

        return jsonify(
            {
                "error": (
                    "Persistenza non disponibile: "
                    f"{error}"
                )
            }
        ), 500

    try:
        _index_observations(
            [observation]
        )

    except (
        OSError,
        ValueError,
        requests.RequestException,
    ) as error:
        app.logger.exception(
            (
                "Osservazione salvata ma "
                "indicizzazione AI non "
                "disponibile: %s"
            ),
            error,
        )

    return jsonify(
        observation
    ), 201


@app.route(
    "/api/observations",
    methods=["GET"],
)
def list_observations():
    try:
        observations = (
            load_observations()
        )

    except (OSError, ValueError) as error:
        app.logger.exception(
            "Impossibile leggere "
            "le osservazioni"
        )

        return jsonify(
            {
                "error": (
                    "Persistenza non disponibile: "
                    f"{error}"
                )
            }
        ), 500

    return jsonify(
        {
            "count": len(observations),
            "observations": observations,
        }
    )


@app.route(
    "/api/economics/simulate",
    methods=["POST"],
)
def simulate_economics():
    data = request.get_json(
        silent=True
    )

    if not isinstance(data, dict):
        return jsonify(
            {
                "error": (
                    "JSON non valido"
                )
            }
        ), 400

    try:
        transactions = int(
            data.get(
                "transactions",
                0,
            )
        )

        average_ticket = float(
            data.get(
                "average_ticket",
                0,
            )
        )

        zorgax_pro_users = int(
            data.get(
                "zorgax_pro_users",
                0,
            )
        )

        zorgax_developer_users = int(
            data.get(
                "zorgax_developer_users",
                0,
            )
        )

        marketplace_commission_percent = float(
            data.get(
                "marketplace_commission_percent",
                2.0,
            )
        )

        payment_fee_percent = float(
            data.get(
                "payment_fee_percent",
                0.0,
            )
        )

        payment_fee_fixed = float(
            data.get(
                "payment_fee_fixed",
                0.0,
            )
        )

        ai_monthly_cost = float(
            data.get(
                "ai_monthly_cost",
                0.0,
            )
        )

        hosting_monthly_cost = float(
            data.get(
                "hosting_monthly_cost",
                0.0,
            )
        )

        other_monthly_cost = float(
            data.get(
                "other_monthly_cost",
                0.0,
            )
        )

        result = simulate_revenue(
            transactions=transactions,
            average_ticket=average_ticket,
            zorgax_pro_users=(
                zorgax_pro_users
            ),
            zorgax_developer_users=(
                zorgax_developer_users
            ),
            marketplace_commission_percent=(
                marketplace_commission_percent
            ),
            payment_fee_percent=(
                payment_fee_percent
            ),
            payment_fee_fixed=(
                payment_fee_fixed
            ),
            ai_monthly_cost=(
                ai_monthly_cost
            ),
            hosting_monthly_cost=(
                hosting_monthly_cost
            ),
            other_monthly_cost=(
                other_monthly_cost
            ),
        )

    except (TypeError, ValueError):
        return jsonify(
            {
                "error": (
                    "I valori della simulazione "
                    "devono essere numerici "
                    "e non negativi"
                )
            }
        ), 400

    return jsonify(result), 200


@app.route(
    "/api/ledger/revenue",
    methods=["POST"],
)
def create_revenue_event():
    data = request.get_json(
        silent=True
    )

    if not isinstance(data, dict):
        return jsonify(
            {
                "error": (
                    "Corpo JSON obbligatorio"
                )
            }
        ), 400

    try:
        amount = float(
            data["amount"]
        )

        currency = str(
            data["currency"]
        ).strip()

        source = (
            normalize_revenue_source(
                data["source"]
            )
        )

        allocations_data = (
            data["allocations"]
        )

    except (
        KeyError,
        TypeError,
        ValueError,
    ):
        return jsonify(
            {
                "error": (
                    "source, amount, currency "
                    "e allocations sono "
                    "obbligatori"
                )
            }
        ), 400

    if (
        not source
        or not currency
        or amount < 0
        or not isinstance(
            allocations_data,
            list,
        )
    ):
        return jsonify(
            {
                "error": (
                    "Dati revenue non validi"
                )
            }
        ), 400

    try:
        allocations = tuple(
            Allocation(
                participant_id=str(
                    item[
                        "participant_id"
                    ]
                ).strip(),
                percentage=float(
                    item["percentage"]
                ),
            )
            for item in allocations_data
        )

        validate_allocations(
            allocations
        )

        amounts = calculate_allocations(
            amount,
            allocations,
        )

    except (
        KeyError,
        TypeError,
        ValueError,
    ) as error:
        return jsonify(
            {
                "error": (
                    "Allocazioni non valide: "
                    f"{error}"
                )
            }
        ), 400

    event = RevenueEvent(
        event_id=str(
            data.get("event_id")
            or uuid.uuid4()
        ),
        source=source,
        amount=amount,
        currency=currency,
        allocations=allocations,
        status=str(
            data.get("status")
            or "RECORDED"
        ),
    )

    record = event.to_dict()
    record[
        "calculated_amounts"
    ] = amounts

    try:
        ledger = load_ledger()

        if any(
            item.get("event_id")
            == record["event_id"]
            for item in ledger
        ):
            return jsonify(
                {
                    "error": (
                        "event_id già presente "
                        "nel ledger"
                    )
                }
            ), 409

        ledger.append(record)
        save_ledger(ledger)

    except (
        OSError,
        ValueError,
    ) as error:
        app.logger.exception(
            "Impossibile salvare "
            "il revenue event"
        )

        return jsonify(
            {
                "error": (
                    "Ledger non disponibile: "
                    f"{error}"
                )
            }
        ), 500

    return jsonify(
        record
    ), 201


@app.route(
    "/api/ledger/assets",
    methods=["POST"],
)
def create_asset_event():
    data = request.get_json(
        silent=True
    )

    if not isinstance(data, dict):
        return jsonify(
            {
                "error": (
                    "Corpo JSON obbligatorio"
                )
            }
        ), 400

    asset_id = data.get("asset_id")
    asset_type = data.get("asset_type")
    creator_id = data.get(
        "creator_id"
    )

    if not all(
        isinstance(value, str)
        and value.strip()
        for value in (
            asset_id,
            asset_type,
            creator_id,
        )
    ):
        return jsonify(
            {
                "error": (
                    "asset_id, asset_type e "
                    "creator_id sono obbligatori"
                )
            }
        ), 400

    event = AssetCreatedEvent(
        event_id=str(
            data.get("event_id")
            or uuid.uuid4()
        ),
        asset_id=asset_id.strip(),
        asset_type=asset_type.strip(),
        creator_id=creator_id.strip(),
        provenance_status=str(
            data.get(
                "provenance_status"
            )
            or "RECORDED"
        ),
    )

    record = event.to_dict()

    try:
        ledger = load_ledger()

        if any(
            item.get("event_id")
            == record["event_id"]
            for item in ledger
        ):
            return jsonify(
                {
                    "error": (
                        "event_id già presente "
                        "nel ledger"
                    )
                }
            ), 409

        ledger.append(record)
        save_ledger(ledger)

    except (
        OSError,
        ValueError,
    ) as error:
        app.logger.exception(
            "Impossibile salvare "
            "l'asset event"
        )

        return jsonify(
            {
                "error": (
                    "Ledger non disponibile: "
                    f"{error}"
                )
            }
        ), 500

    return jsonify(
        record
    ), 201


@app.route(
    "/api/ledger/revenue",
    methods=["GET"],
)
def list_revenue_events():
    try:
        events = [
            event
            for event in load_ledger()
            if event.get(
                "event_type"
            ) == "REVENUE"
        ]

    except (
        OSError,
        ValueError,
    ) as error:
        app.logger.exception(
            "Impossibile leggere "
            "il revenue ledger"
        )

        return jsonify(
            {
                "error": (
                    "Ledger non disponibile: "
                    f"{error}"
                )
            }
        ), 500

    return jsonify(
        {
            "count": len(events),
            "events": events,
        }
    )


@app.route(
    "/api/ledger/assets",
    methods=["GET"],
)
def list_asset_events():
    try:
        events = [
            event
            for event in load_ledger()
            if event.get(
                "event_type"
            ) == "ASSET_CREATED"
        ]

    except (
        OSError,
        ValueError,
    ) as error:
        app.logger.exception(
            "Impossibile leggere "
            "gli asset ledger"
        )

        return jsonify(
            {
                "error": (
                    "Ledger non disponibile: "
                    f"{error}"
                )
            }
        ), 500

    return jsonify(
        {
            "count": len(events),
            "events": events,
        }
    )


@app.route(
    "/api/ledger/balances",
    methods=["GET"],
)
def list_ledger_balances():
    try:
        balances = (
            calculate_balance_breakdown(
                load_ledger()
            )
        )

    except (
        OSError,
        ValueError,
        TypeError,
    ) as error:
        app.logger.exception(
            "Impossibile calcolare "
            "i balance"
        )

        return jsonify(
            {
                "error": (
                    "Ledger non disponibile: "
                    f"{error}"
                )
            }
        ), 500

    participants = [
        {
            "participant_id": (
                participant_id
            ),
            **details,
        }
        for participant_id, details
        in sorted(
            balances.items()
        )
    ]

    return jsonify(
        {
            "participants": (
                participants
            ),
        }
    )


@app.route(
    "/api/ledger",
    methods=["GET"],
)
def list_ledger():
    try:
        events = load_ledger()

    except (
        OSError,
        ValueError,
    ) as error:
        app.logger.exception(
            "Impossibile leggere "
            "il ledger"
        )

        return jsonify(
            {
                "error": (
                    "Ledger non disponibile: "
                    f"{error}"
                )
            }
        ), 500

    return jsonify(
        {
            "count": len(events),
            "events": events,
        }
    )


def _authoritative_metadata_answer(
    question,
    context,
):
    if not context:
        return None

    metadata = context[0].get(
        "metadata"
    )

    if not isinstance(
        metadata,
        dict,
    ):
        return None

    question_lower = (
        question.lower()
    )

    parts = []

    if (
        "status" in metadata
        and any(
            term in question_lower
            for term in (
                "stato",
                "status",
            )
        )
    ):
        parts.append(
            f"Stato: {metadata['status']}."
        )

    if (
        "onchainRecorded" in metadata
        and any(
            term in question_lower
            for term in (
                "blockchain",
                "onchain",
                "on-chain",
            )
        )
    ):
        value = metadata[
            "onchainRecorded"
        ]

        if isinstance(value, bool):
            parts.append(
                "Registrazione blockchain: "
                + (
                    "SI."
                    if value
                    else "no."
                )
            )

    if (
        "paymentRequired" in metadata
        and any(
            term in question_lower
            for term in (
                "pagamento",
                "payment",
            )
        )
    ):
        value = metadata[
            "paymentRequired"
        ]

        if isinstance(value, bool):
            parts.append(
                "Pagamento richiesto: "
                + (
                    "SI."
                    if value
                    else "no."
                )
            )

    if (
        "success" in metadata
        and any(
            term in question_lower
            for term in (
                "successo",
                "success",
                "riuscito",
            )
        )
    ):
        value = metadata["success"]

        if isinstance(value, bool):
            parts.append(
                "Operazione riuscita: "
                + (
                    "SI."
                    if value
                    else "no."
                )
            )

    return (
        " ".join(parts)
        if parts
        else None
    )

@app.route("/knowledge-proof-verifier", methods=["GET"])
def knowledge_proof_verifier_page():
    """Serve the visual Knowledge Proof verifier."""
    with open(os.path.join(os.path.dirname(__file__), "knowledge_proof_verifier.html"), encoding="utf-8") as handle:
        return handle.read()


@app.route("/api/proofs/knowledge-card/verify", methods=["POST"])
def verify_knowledge_card_proof():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Corpo JSON obbligatorio"}), 400

    payload = data.get("payload")
    contract_address = data.get("contract_address")
    expected_hash = data.get("expected_hash")

    if not isinstance(payload, str) or not payload.strip():
        return jsonify({"error": "payload obbligatorio"}), 400
    if not isinstance(contract_address, str) or not contract_address.strip():
        return jsonify({"error": "contract_address obbligatorio"}), 400

    payload_path = os.path.abspath(os.path.join(PROJECT_ROOT, payload.strip()))
    project_root = os.path.abspath(PROJECT_ROOT)
    if os.path.commonpath([project_root, payload_path]) != project_root:
        return jsonify({"error": "payload fuori dal repository"}), 400
    if not os.path.isfile(payload_path):
        return jsonify({"error": "payload non trovato"}), 404

    try:
        result = verify_knowledge_proof(
            payload_path,
            contract_address.strip(),
            expected_hash=expected_hash,
            rpc_url=os.environ.get("SEPOLIA_RPC_URL", "https://ethereum-sepolia-rpc.publicnode.com"),
            timeout=min(AI_REQUEST_TIMEOUT, 30),
        )
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except requests.RequestException:
        app.logger.exception("Ethereum Sepolia RPC non raggiungibile")
        return jsonify({"error": "Ethereum Sepolia temporaneamente non disponibile"}), 503

    result["payload"] = os.path.relpath(payload_path, project_root).replace(os.sep, "/")
    return jsonify(result)


@app.route("/api/ai/ask", methods=["POST"])
def ask_ai():
    data = request.get_json(
        silent=True
    )

    if not isinstance(data, dict):
        return jsonify(
            {
                "error": (
                    "Corpo JSON obbligatorio"
                )
            }
        ), 400

    if (
        data.get("topic")
        == "nicola-comics"
    ):
        return answer_catalog(data)

    question = data.get(
        "question"
    )

    if (
        not isinstance(question, str)
        or not question.strip()
    ):
        return jsonify(
            {
                "error": (
                    "Domanda obbligatoria"
                )
            }
        ), 400

    question = question.strip()

    if (
        len(question)
        > AI_MAX_QUESTION_LENGTH
    ):
        return jsonify(
            {
                "error": (
                    "Domanda troppo lunga"
                )
            }
        ), 400

    try:
        context = (
            _search_observations(
                question
            )
        )

        answer = (
            _authoritative_metadata_answer(
                question,
                context,
            )
        )

        if answer is None:
            answer = _generate_answer(
                question,
                context,
            )

    except (
        OSError,
        ValueError,
    ) as error:
        app.logger.exception(
            "Errore durante "
            "la richiesta AI"
        )

        return jsonify(
            {
                "error": (
                    "Risposta AI non "
                    "disponibile: "
                    f"{error}"
                )
            }
        ), 502

    except requests.RequestException:
        app.logger.exception(
            "Ollama o Qdrant "
            "non raggiungibile"
        )

        return jsonify(
            {
                "error": (
                    "Servizio AI "
                    "temporaneamente "
                    "non disponibile"
                )
            }
        ), 503

    return jsonify(
        {
            "answer": answer,
            "model": OLLAMA_MODEL,
            "embedding_model": (
                OLLAMA_EMBEDDING_MODEL
            ),
            "sources": context,
        }
    )


@app.route("/v1/models", methods=["GET"])
def openai_models():
    return jsonify(
        {
            "object": "list",
            "data": [
                {
                    "id": "myzubster-rag",
                    "object": "model",
                    "owned_by": "myzubster",
                }
            ],
        }
    )


@app.route("/v1/chat/completions", methods=["POST"])
def openai_chat_completions():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify(
            {
                "error": {
                    "message": "Corpo JSON obbligatorio",
                    "type": "invalid_request_error",
                }
            }
        ), 400

    messages = data.get("messages")

    if not isinstance(messages, list):
        return jsonify(
            {
                "error": {
                    "message": "messages obbligatorio",
                    "type": "invalid_request_error",
                }
            }
        ), 400

    question = None

    for message in reversed(messages):
        if (
            isinstance(message, dict)
            and message.get("role") == "user"
            and isinstance(message.get("content"), str)
            and message["content"].strip()
        ):
            question = message["content"].strip()
            break

    if question is None:
        return jsonify(
            {
                "error": {
                    "message": "Messaggio utente obbligatorio",
                    "type": "invalid_request_error",
                }
            }
        ), 400

    if len(question) > AI_MAX_QUESTION_LENGTH:
        return jsonify(
            {
                "error": {
                    "message": "Domanda troppo lunga",
                    "type": "invalid_request_error",
                }
            }
        ), 400

    try:
        context = _search_observations(question)

        answer = _authoritative_metadata_answer(
            question,
            context,
        )

        if answer is None:
            answer = _generate_answer(
                question,
                context,
            )

    except (OSError, ValueError) as error:
        app.logger.exception(
            "Errore durante la richiesta OpenAI-compatible"
        )

        return jsonify(
            {
                "error": {
                    "message": (
                        "Risposta AI non disponibile: "
                        f"{error}"
                    ),
                    "type": "server_error",
                }
            }
        ), 502

    except requests.RequestException:
        app.logger.exception(
            "Ollama o Qdrant non raggiungibile"
        )

        return jsonify(
            {
                "error": {
                    "message": (
                        "Servizio AI temporaneamente "
                        "non disponibile"
                    ),
                    "type": "server_error",
                }
            }
        ), 503

    return jsonify(
        {
            "id": "chatcmpl-myzubster",
            "object": "chat.completion",
            "model": "myzubster-rag",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": answer,
                    },
                    "finish_reason": "stop",
                }
            ],
        }
    )


if __name__ == "__main__":
    app.run(
        host=os.environ.get(
            "MYZUBSTER_HOST",
            "127.0.0.1",
        ),
        port=int(
            os.environ.get(
                "MYZUBSTER_PORT",
                "5000",
            )
        ),
        debug=False,
    )