import requests
import time

BASE_URL = "http://127.0.0.1:5000"

def test_full_workflow():
    # 1. Crea osservazione
    r = requests.post(
        f"{BASE_URL}/api/observation",
        json={
            'description': 'Test completo',
            'latitude': 45.464,
            'longitude': 9.190
        }
    )
    assert r.status_code == 200, f"POST failed: {r.status_code}"
    assert 'id' in r.text, "POST response should contain an id"

    # 2. Recupera osservazioni (breve attesa per il salvataggio)
    time.sleep(1)
    r2 = requests.get(f"{BASE_URL}/api/observations")
    assert r2.status_code == 200, f"GET failed: {r2.status_code}"
    assert 'observations' in r2.text.lower() or '[' in r2.text
