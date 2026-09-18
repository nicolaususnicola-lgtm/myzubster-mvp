from hashlib import sha256
from pathlib import Path

import requests

OLLAMA_URL = "http://localhost:11434/api/embed"
QDRANT_URL = "http://localhost:6333"
COLLECTION = "myzubster"
MODEL = "nomic-embed-text"
TIMEOUT = 120

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150


def deterministic_id(value):
    digest = sha256(value.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") & ((1 << 63) - 1)


def chunks(text):
    start = 0

    while start < len(text):
        end = min(start + CHUNK_SIZE, len(text))
        chunk = text[start:end].strip()

        if chunk:
            yield start, chunk

        if end >= len(text):
            break

        start = end - CHUNK_OVERLAP


def embedding(text):
    response = requests.post(
        OLLAMA_URL,
        json={"model": MODEL, "input": text},
        timeout=TIMEOUT,
    )
    response.raise_for_status()

    data = response.json()
    embeddings = data.get("embeddings")

    if not embeddings or not embeddings[0]:
        raise ValueError("Ollama non ha restituito un embedding valido")

    return embeddings[0]


def upsert(point):
    response = requests.put(
        f"{QDRANT_URL}/collections/{COLLECTION}/points?wait=true",
        json={"points": [point]},
        timeout=TIMEOUT,
    )
    response.raise_for_status()


def delete_existing_knowledge():
    response = requests.post(
        f"{QDRANT_URL}/collections/{COLLECTION}/points/delete?wait=true",
        json={
            "filter": {
                "must": [
                    {
                        "key": "observation.type",
                        "match": {"value": "knowledge"},
                    }
                ]
            }
        },
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    print("Removed previous knowledge points from Qdrant")


delete_existing_knowledge()

loaded = 0
skipped = 0

for file in sorted(Path("knowledge").glob("*.md")):
    text = file.read_text(encoding="utf-8").strip()

    if not text:
        print(f"SKIP empty: {file}")
        skipped += 1
        continue

    source = file.as_posix()

    for chunk_index, (offset, chunk) in enumerate(chunks(text)):
        key = f"{source}:chunk:{chunk_index}"

        observation = {
            "id": f"knowledge:{file.stem}:{chunk_index}",
            "description": chunk,
            "coordinates": {},
            "timestamp": "n/d",
            "type": "knowledge",
            "title": file.stem,
            "source": source,
            "chunk": chunk_index,
            "offset": offset,
        }

        point = {
            "id": deterministic_id(key),
            "vector": embedding(chunk),
            "payload": {
                "observation": observation
            },
        }

        upsert(point)

        loaded += 1
        print(
            f"OK: {source} "
            f"chunk={chunk_index} chars={len(chunk)}"
        )


print(
    f"Loaded {loaded} knowledge chunks; "
    f"skipped {skipped} empty documents"
)

