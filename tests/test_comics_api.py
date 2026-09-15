import hashlib
from pathlib import Path
from unittest.mock import patch

import pytest

from src.api.server import app


@pytest.fixture
def client():
    return app.test_client()


def test_complete_catalog_path_without_ai_services(client):
    with patch("requests.request", side_effect=AssertionError("No AI network calls")):
        response = client.post("/api/zorgax/ask", json={"question": "Mostrami i fumetti di Nicola"})
        assert response.status_code == 200
        entries = response.json["sources"]
        assert len(entries) == 3
        for entry in entries:
            detail = client.get(entry["detail_url"])
            assert detail.status_code == 200
            assert detail.json["comic_id"] == entry["comic_id"]
            path = Path(__file__).resolve().parents[1] / entry["asset_path"].split(":", 1)[1]
            raw = path.read_bytes()
            assert hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest() == entry["source_hash"]
            assert entry["transaction_hash"] is None
            assert entry["rights_status"] == "TO_VERIFY"


def test_references_are_explicit_opt_in(client):
    assert client.get("/api/comics").json["count"] == 3
    assert client.get("/api/comics?include_references=true").json["count"] == 6


def test_candidate_is_proposal_and_not_minted(client):
    response = client.post("/api/zorgax/ask", json={"question": "Quale candidata?", "action": "candidate"})
    assert response.status_code == 200
    assert [c["comic_id"] for c in response.json["sources"]] == ["n4k48-comic-001"]
    assert response.json["sources"][0]["selection_status"] == "PROPOSED_FOR_REVIEW"
    assert "non una prova di mint" in response.json["notice"]


def test_existing_ai_api_routes_explicit_topic(client):
    with patch("src.api.server._generate_answer", side_effect=AssertionError("Do not call Ollama")):
        response = client.post("/api/ai/ask", json={"topic": "nicola-comics", "question": "Scheda", "action": "detail", "comic_id": "n4k48-comic-002"})
    assert response.status_code == 200
    assert response.json["sources"][0]["comic_id"] == "n4k48-comic-002"


@pytest.mark.parametrize("payload,status", [
    (None, 400), ([], 400), ({}, 400),
    ({"question": "x" * 2001}, 400),
    ({"question": "Ciao", "action": "mint"}, 400),
    ({"question": "Ciao", "action": "detail"}, 400),
    ({"question": "Ciao", "action": "detail", "comic_id": "missing"}, 404),
])
def test_invalid_requests(client, payload, status):
    assert client.post("/api/zorgax/ask", json=payload).status_code == status


def test_unknown_detail(client):
    assert client.get("/api/comics/not-found").status_code == 404


def test_missing_catalog_is_controlled(client):
    with patch("src.api.comics.load_catalog", side_effect=OSError("private/path")):
        response = client.post("/api/zorgax/ask", json={"question": "Galleria"})
        assert response.status_code == 503
        assert "private/path" not in response.get_data(as_text=True)


def test_next_steps_preserve_public_integration_boundary(client):
    response = client.post("/api/zorgax/ask", json={"question": "Come continuo?", "action": "next_steps"})
    assert response.status_code == 200
    assert "Zorgax pubblico" in response.json["answer"]
