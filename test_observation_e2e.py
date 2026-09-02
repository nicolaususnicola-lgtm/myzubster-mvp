import json

import persistence_helper
from src.api.server import app


def test_create_persist_read_observation(tmp_path, monkeypatch):
    observations_file = tmp_path / "observations.json"
    monkeypatch.setattr(persistence_helper, "OBS_FILE", str(observations_file))
    client = app.test_client()

    create_response = client.post(
        "/api/observation",
        json={
            "description": "Albero urbano verificato",
            "latitude": 45.464,
            "longitude": 9.190,
            "media_hash": "QmEvidence123",
        },
    )

    assert create_response.status_code == 201
    created = create_response.get_json()
    assert created["id"]
    assert created["description"] == "Albero urbano verificato"

    persisted = json.loads(observations_file.read_text(encoding="utf-8"))
    assert persisted == [created]

    read_response = client.get("/api/observations")
    assert read_response.status_code == 200
    assert read_response.get_json() == {
        "count": 1,
        "observations": [created],
    }


def test_create_rejects_invalid_input(tmp_path, monkeypatch):
    monkeypatch.setattr(
        persistence_helper, "OBS_FILE", str(tmp_path / "observations.json")
    )
    client = app.test_client()

    assert client.post("/api/observation").status_code == 400
    assert client.post("/api/observation", json={"description": ""}).status_code == 400
    assert client.post(
        "/api/observation",
        json={"description": "Test", "latitude": 91, "longitude": 0},
    ).status_code == 400
