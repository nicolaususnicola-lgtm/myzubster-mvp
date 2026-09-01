import requests
import time

# 1. Crea osservazione
r = requests.post('http://127.0.0.1:5000/api/observation', json={
    'description': 'Test completo',
    'latitude': 45.464,
    'longitude': 9.190
})
print(f"POST status: {r.status_code}")
print(r.text)

# 2. Recupera osservazioni (il server deve essere ancora attivo)
r2 = requests.get('http://127.0.0.1:5000/api/observations')
print(f"\nGET status: {r2.status_code}")
print(r2.text)
