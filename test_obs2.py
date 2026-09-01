import requests

BASE_URL = "http://127.0.0.1:5000"

def test_create_observation_with_media():
    r = requests.post(
        f"{BASE_URL}/api/observation",
        json={
            'description': 'Osservazione con media',
            'latitude': 41.9028,
            'longitude': 12.4964,
            'media_hash': 'QmTest123456789'
        }
    )
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
