import requests

BASE_URL = "http://127.0.0.1:5000"

def test_create_observation():
    r = requests.post(
        f"{BASE_URL}/api/observation",
        json={
            'description': 'Prova',
            'latitude': 45.464,
            'longitude': 9.190
        }
    )
    # Accetta sia 200 (OK) che 201 (Created)
    assert r.status_code in (200, 201), f"Expected 200 or 201, got {r.status_code}"
    assert 'id' in r.text or '"id"' in r.text, "Response should contain id"

def test_create_observation_with_media_hash():
    r = requests.post(
        f"{BASE_URL}/api/observation",
        json={
            'description': 'Seconda osservazione di test',
            'latitude': 41.9028,
            'longitude': 12.4964,
            'media_hash': 'QmTest123456789'
        }
    )
    assert r.status_code in (200, 201), f"Expected 200 or 201, got {r.status_code}"
    assert 'success' in r.text.lower() or 'id' in r.text or '"id"' in r.text
