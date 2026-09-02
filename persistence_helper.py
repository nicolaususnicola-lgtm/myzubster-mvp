import json
import os
from pathlib import Path


OBS_FILE = os.environ.get("MYZUBSTER_OBSERVATIONS_FILE", "observations.json")


def _observations_path():
    return Path(OBS_FILE)


def load_observations():
    path = _observations_path()
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as stream:
        data = json.load(stream)
    if not isinstance(data, list):
        raise ValueError("Il file delle osservazioni deve contenere una lista")
    return data


def save_observations(observations):
    path = _observations_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_suffix(f"{path.suffix}.tmp")
    with temporary_path.open("w", encoding="utf-8") as stream:
        json.dump(observations, stream, ensure_ascii=False, indent=2)
    temporary_path.replace(path)
