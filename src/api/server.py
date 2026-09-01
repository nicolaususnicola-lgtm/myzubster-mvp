# -*- coding: utf-8 -*-
import json
import os
import sys
from flask import Flask, request, jsonify
from datetime import datetime

# Aggiungi la cartella principale al percorso
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.core.observation import Observation
from persistence_helper import load_observations, save_observations

app = Flask(__name__)

@app.route('/api/observation', methods=['POST'])
def create_observation():
    try:
        data = request.get_json()
        
        # Validazione base
        if not data.get('description'):
            return jsonify({'error': 'Descrizione obbligatoria'}), 400
        
        # Crea la nuova osservazione
        obs = Observation(
            description=data['description'],
            latitude=float(data.get('latitude', 0)),
            longitude=float(data.get('longitude', 0)),
            media_hash=data.get('media_hash', '')
        )
        
        obs_dict = obs.to_dict()
        
        # Carica osservazioni esistenti, aggiungi nuova, salva
        observations = load_observations()
        observations.append(obs_dict)
        save_observations(observations)
        
        return jsonify(obs_dict), 201
        
    except Exception as e:
        return jsonify({'error': f'Errore interno: {str(e)}'}), 500

@app.route('/api/observations', methods=['GET'])
def list_observations():
    observations = load_observations()
    return jsonify({'count': len(observations), 'observations': observations})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
