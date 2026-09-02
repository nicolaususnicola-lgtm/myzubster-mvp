import os
import sys

from flask import Flask, jsonify, request


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from persistence_helper import load_observations, save_observations
from src.core.observation import Observation


app = Flask(__name__)


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


if __name__ == "__main__":
    app.run(
        host=os.environ.get("MYZUBSTER_HOST", "127.0.0.1"),
        port=int(os.environ.get("MYZUBSTER_PORT", "5000")),
        debug=False,
    )
