import requests
r = requests.post('http://127.0.0.1:5000/api/observation', json={
    'description': 'Seconda osservazione di test',
    'latitude': 41.9028,
    'longitude': 12.4964,
    'media_hash': 'QmTest123456789'
})
print("Status:", r.status_code)
print(r.text)
