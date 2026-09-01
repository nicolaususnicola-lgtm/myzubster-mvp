import requests

BASE_URL = "http://127.0.0.1:5000"

def test_get_observations():
    r = requests.get(f"{BASE_URL}/api/observations")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    assert 'observations' in r.text.lower() or '[' in r.text

def test_get_observations_timeout():
    r = requests.get(f"{BASE_URL}/api/observations", timeout=5)
    assert r.status_code == 200
