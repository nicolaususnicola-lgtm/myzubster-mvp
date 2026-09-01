import json
import os

OBS_FILE = 'observations.json'

def load_observations():
    if os.path.exists(OBS_FILE):
        with open(OBS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_observations(observations):
    with open(OBS_FILE, 'w') as f:
        json.dump(observations, f, indent=2)
