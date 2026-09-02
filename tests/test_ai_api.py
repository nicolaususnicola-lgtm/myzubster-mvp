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
@patch("src.api.server._index_and_search")
@patch("src.api.server.load_observations")
def test_ai_ask_returns_grounded_answer(load, search, generate):
    observation = {"id": "1", "description": "Osservazione di prova"}
    load.return_value = [observation]
    search.return_value = [observation]

    client = app.test_client()
    response = client.post("/api/ai/ask", json={"question": "Cosa è stato osservato?"})

    assert response.status_code == 200
    assert response.get_json()["answer"] == "Risposta verificata"
    assert response.get_json()["sources"] == [observation]
    search.assert_called_once_with("Cosa è stato osservato?", [observation])
    generate.assert_called_once_with("Cosa è stato osservato?", [observation])
