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
    text_length = len(text)

    while start < text_length:
        hard_end = min(start + CHUNK_SIZE, text_length)
        end = hard_end

        if hard_end < text_length:
            window = text[start:hard_end]

            # Preferisci la fine di un paragrafo.
            paragraph_break = window.rfind("\n\n")

            # Altrimenti usa la fine di una riga.
            line_break = window.rfind("\n")

            # Evita chunk troppo piccoli.
            minimum_break = int(CHUNK_SIZE * 0.6)

            if paragraph_break >= minimum_break:
                end = start + paragraph_break
            elif line_break >= minimum_break:
                end = start + line_break

        chunk = text[start:end].strip()

        if chunk:
            yield start, chunk

        if end >= text_length:
            break

        # Mantieni l'overlap, ma cerca di ripartire
        # dall'inizio di una riga.
        next_start = max(0, end - CHUNK_OVERLAP)

        newline = text.find("\n", next_start, end)

        if newline != -1:
            next_start = newline + 1

        # Protezione contro eventuali loop infiniti.
        if next_start <= start:
            next_start = end

        start = next_start


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
        raise ValueError(
            "Ollama non ha restituito un embedding valido"
        )

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