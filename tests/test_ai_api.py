from unittest.mock import patch

from src.api.server import app


def test_ai_ask_requires_json():
    client = app.test_client()
    response = client.post("/api/ai/ask")
    assert response.status_code == 400
    assert response.get_json()["error"] == "Corpo JSON obbligatorio"


def test_ai_ask_requires_question():
    client = app.test_client()
    response = client.post("/api/ai/ask", json={"question": "   "})
    assert response.status_code == 400
    assert response.get_json()["error"] == "Domanda obbligatoria"


@patch("src.api.server._generate_answer", return_value="Risposta verificata")
@patch("src.api.server._search_observations")
def test_ai_ask_returns_grounded_answer(search, generate):
    observation = {"id": "1", "description": "Osservazione di prova"}
    search.return_value = [observation]

    client = app.test_client()
    response = client.post("/api/ai/ask", json={"question": "Cosa Ã¨ stato osservato?"})

    assert response.status_code == 200
    assert response.get_json()["answer"] == "Risposta verificata"
    assert response.get_json()["sources"] == [observation]
    search.assert_called_once_with("Cosa Ã¨ stato osservato?")
    generate.assert_called_once_with("Cosa Ã¨ stato osservato?", [observation])

@patch("src.api.server._index_observations")
@patch("src.api.server.save_observations")
@patch("src.api.server.load_observations", return_value=[])
def test_create_observation_preserves_structured_metadata(load, save, index):
    client = app.test_client()

    metadata = {
        "status": "RECORDED",
        "success": True,
        "paymentRequired": False,
        "onchainRecorded": False,
    }

    response = client.post(
        "/api/observation",
        json={
            "description": "Osservazione strutturata di prova",
            "latitude": 0,
            "longitude": 0,
            "metadata": metadata,
        },
    )

    assert response.status_code == 201

    observation = response.get_json()
    assert observation["metadata"] == metadata
    assert observation["metadata"]["status"] == "RECORDED"
    assert observation["metadata"]["success"] is True
    assert observation["metadata"]["paymentRequired"] is False
    assert observation["metadata"]["onchainRecorded"] is False

    save.assert_called_once()
    index.assert_called_once_with([observation])

@patch("src.api.server._request_json")
def test_generate_answer_sends_structured_metadata_to_ollama(request_json):
    request_json.return_value = {
        "message": {"content": "Non registrato su blockchain."}
    }

    observation = {
        "id": "1",
        "description": "Passaggio registrato nel sistema MyZubster.",
        "metadata": {
            "status": "RECORDED",
            "success": True,
            "paymentRequired": False,
            "onchainRecorded": False,
        },
    }

    from src.api.server import _generate_answer

    answer = _generate_answer(
        "Il passaggio è registrato su blockchain?",
        [observation],
    )

    assert answer == "Non registrato su blockchain."

    request_json.assert_called_once()
    payload = request_json.call_args.kwargs["json"]
    prompt = payload["messages"][1]["content"]

    assert '"status": "RECORDED"' in prompt
    assert '"success": true' in prompt
    assert '"paymentRequired": false' in prompt
    assert '"onchainRecorded": false' in prompt


@patch("src.api.server.save_ledger")
@patch("src.api.server.load_ledger", return_value=[])
def test_create_revenue_event_persists_explicit_allocations(load, save):
    client = app.test_client()
    response = client.post(
        "/api/ledger/revenue",
        json={
            "event_id": "rev-api-001",
            "source": "MYZUBSTER_ONLINE",
            "amount": 1000,
            "currency": "EUR",
            "allocations": [
                {"participant_id": "daniel", "percentage": 2},
                {"participant_id": "nicola", "percentage": 98},
            ],
        },
    )

    assert response.status_code == 201
    event = response.get_json()
    assert event["event_type"] == "REVENUE"
    assert event["calculated_amounts"] == {"daniel": 20.0, "nicola": 980.0}
    save.assert_called_once_with([event])


@patch("src.api.server.save_ledger")
@patch("src.api.server.load_ledger", return_value=[])
def test_create_nft_asset_event_persists_creator_provenance(load, save):
    client = app.test_client()
    response = client.post(
        "/api/ledger/assets",
        json={
            "event_id": "asset-api-001",
            "asset_id": "n4k48-comic-001",
            "asset_type": "NFT",
            "creator_id": "nicola",
        },
    )

    assert response.status_code == 201
    event = response.get_json()
    assert event["event_type"] == "ASSET_CREATED"
    assert event["creator_id"] == "nicola"
    assert event["asset_type"] == "NFT"
    assert event["provenance_status"] == "RECORDED"
    save.assert_called_once_with([event])


@patch("src.api.server.load_ledger")
def test_list_revenue_events_returns_only_revenue(load):
    load.return_value = [
        {"event_type": "REVENUE", "event_id": "rev-1"},
        {"event_type": "ASSET_CREATED", "event_id": "asset-1"},
    ]
    response = app.test_client().get("/api/ledger/revenue")
    assert response.status_code == 200
    assert response.get_json() == {
        "count": 1,
        "events": [{"event_type": "REVENUE", "event_id": "rev-1"}],
    }


@patch("src.api.server.load_ledger")
def test_list_asset_events_returns_only_assets(load):
    load.return_value = [
        {"event_type": "REVENUE", "event_id": "rev-1"},
        {"event_type": "ASSET_CREATED", "event_id": "asset-1", "asset_id": "n4k48-comic-001"},
    ]
    response = app.test_client().get("/api/ledger/assets")
    assert response.status_code == 200
    assert response.get_json() == {
        "count": 1,
        "events": [
            {
                "event_type": "ASSET_CREATED",
                "event_id": "asset-1",
                "asset_id": "n4k48-comic-001",
            }
        ],
    }
