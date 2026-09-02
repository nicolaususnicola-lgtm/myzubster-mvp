import os
import sys
from urllib.parse import quote

import requests
from flask import Flask, jsonify, request


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from persistence_helper import load_observations, save_observations
from src.core.observation import Observation


app = Flask(__name__)

OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://host.docker.internal:11434").rstrip("/")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "mistral:latest")
OLLAMA_EMBEDDING_MODEL = os.environ.get("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
QDRANT_URL = os.environ.get("QDRANT_URL", "http://qdrant:6333").rstrip("/")
QDRANT_COLLECTION = os.environ.get("QDRANT_COLLECTION", "myzubster")
AI_REQUEST_TIMEOUT = float(os.environ.get("AI_REQUEST_TIMEOUT", "120"))
AI_CONTEXT_LIMIT = int(os.environ.get("AI_CONTEXT_LIMIT", "5"))
AI_MAX_QUESTION_LENGTH = int(os.environ.get("AI_MAX_QUESTION_LENGTH", "2000"))


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


def _index_and_search(question, observations):
    if not observations:
        return []

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
        return []

    collection = quote(QDRANT_COLLECTION, safe="")
    _request_json(
        "PUT",
        f"{QDRANT_URL}/collections/{collection}/points?wait=true",
        json={"points": points},
    )

    question_vector = _ollama_embedding(question)
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
        f"- {observation.get('description', '')} "
        f"(coordinate: {observation.get('coordinates', {})}, "
        f"data: {observation.get('timestamp', 'n/d')})"
        for observation in context
    )
    if not context_text:
        context_text = "Nessuna osservazione MyZubster disponibile."

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
                        "Sei l'assistente MyZubster. Rispondi in italiano usando soltanto "
                        "il contesto fornito. Se il contesto non contiene la risposta, "
                        "dichiara chiaramente che non ci sono informazioni sufficienti."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Contesto MyZubster:\n{context_text}\n\nDomanda: {question}",
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

    try:
        observations = load_observations()
        observations.append(observation)
        save_observations(observations)
    except (OSError, ValueError) as error:
        app.logger.exception("Impossibile salvare l'osservazione")
        return jsonify({"error": f"Persistenza non disponibile: {error}"}), 500

    return jsonify(observation), 201


@app.route("/api/observations", methods=["GET"])
def list_observations():
    try:
        observations = load_observations()
    except (OSError, ValueError) as error:
        app.logger.exception("Impossibile leggere le osservazioni")
        return jsonify({"error": f"Persistenza non disponibile: {error}"}), 500
    return jsonify({"count": len(observations), "observations": observations})


@app.route("/api/ai/ask", methods=["POST"])
def ask_ai():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Corpo JSON obbligatorio"}), 400

    question = data.get("question")
    if not isinstance(question, str) or not question.strip():
        return jsonify({"error": "Domanda obbligatoria"}), 400

    question = question.strip()
    if len(question) > AI_MAX_QUESTION_LENGTH:
        return jsonify({"error": "Domanda troppo lunga"}), 400

    try:
        observations = load_observations()
        context = _index_and_search(question, observations)
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
