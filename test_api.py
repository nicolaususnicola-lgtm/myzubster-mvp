import requests
r = requests.post('http://127.0.0.1:5000/api/observation', json={'description': 'Prova', 'latitude': 45.464, 'longitude': 9.190})
print(r.status_code)
print(r.text)
