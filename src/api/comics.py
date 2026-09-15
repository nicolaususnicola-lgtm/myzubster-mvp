"""Read-only catalog adapter for the Nicola Comics pilot."""

import json
import os
from pathlib import Path

from flask import Blueprint, current_app, jsonify, request


comics_api = Blueprint("comics", __name__)
MANIFEST = Path(__file__).resolve().parents[2] / "docs/nicola-comics/comics.manifest.json"
GALLERY_URL = "https://github.com/nicolaususnicola-lgtm/myzubster-mvp/blob/main/docs/nicola-comics/GALLERY.md"


def pilot_base_url():
    """Optional public base URL for absolute API links; localhost is never assumed."""
    value = os.getenv("NICOLA_COMICS_BASE_URL", "").strip().rstrip("/")
    if value and not value.startswith(("https://", "http://")):
        current_app.logger.warning("Ignoring invalid NICOLA_COMICS_BASE_URL")
        return ""
    return value


def api_url(path):
    base = pilot_base_url()
    return f"{base}{path}" if base else path


def load_catalog():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("comics"), list):
        raise ValueError("Invalid catalog")
    entries = data["comics"]
    if any(not isinstance(c, dict) or not isinstance(c.get("comic_id"), str)
           or not isinstance(c.get("title"), str) for c in entries):
        raise ValueError("Invalid catalog entry")
    if len({c["comic_id"] for c in entries}) != len(entries):
        raise ValueError("Duplicate comic ID")
    return data


def catalog_error():
    current_app.logger.exception("Comic catalog unavailable")
    return jsonify({"error": "Catalogo fumetti temporaneamente non disponibile"}), 503


def public_entry(entry):
    path = "/api/comics/" + entry["comic_id"]
    return {**entry, "detail_url": api_url(path)}


@comics_api.get("/api/comics")
def list_comics():
    try:
        data = load_catalog()
    except (OSError, ValueError):
        return catalog_error()
    entries = data["comics"]
    if request.args.get("include_references") != "true":
        entries = [c for c in entries if c.get("pilot_relationship") == "CREATED_FOR_NICOLA_PILOT"]
    return jsonify({"project": data.get("project"), "count": len(entries),
                    "comics": [public_entry(c) for c in entries], "gallery_url": GALLERY_URL,
                    "api_base_url": pilot_base_url() or None})


@comics_api.get("/api/comics/<comic_id>")
def comic_detail(comic_id):
    try:
        data = load_catalog()
    except (OSError, ValueError):
        return catalog_error()
    entry = next((c for c in data["comics"] if c["comic_id"] == comic_id), None)
    if entry is None:
        return jsonify({"error": "Fumetto non trovato"}), 404
    return jsonify(public_entry(entry))


def answer_catalog(data):
    """Explicit topic routing; unrelated AI questions keep their existing path."""
    question = data.get("question")
    if not isinstance(question, str) or not question.strip():
        return jsonify({"error": "Domanda obbligatoria"}), 400
    if len(question.strip()) > 2000:
        return jsonify({"error": "Domanda troppo lunga"}), 400
    action = data.get("action", "gallery")
    if action not in ("gallery", "detail", "candidate", "next_steps"):
        return jsonify({"error": "Azione non valida", "actions": ["gallery", "detail", "candidate", "next_steps"]}), 400
    comic_id = data.get("comic_id")
    if action == "detail" and (not isinstance(comic_id, str) or not comic_id):
        return jsonify({"error": "comic_id obbligatorio"}), 400
    try:
        catalog = load_catalog()
    except (OSError, ValueError):
        return catalog_error()
    originals = [c for c in catalog["comics"] if c.get("pilot_relationship") == "CREATED_FOR_NICOLA_PILOT"]
    selected = originals
    if action == "detail":
        selected = [c for c in catalog["comics"] if c["comic_id"] == comic_id]
        if not selected:
            return jsonify({"error": "Fumetto non trovato"}), 404
    elif action == "candidate":
        selected = [c for c in originals if c.get("nft_status") == "NFT_CANDIDATE"]
    if action == "next_steps":
        answer = "Verificare provenienza e autorizzazioni, confermare la candidata e provare il collegamento al Zorgax pubblico con Nicola. Il mint non viene eseguito da questo servizio."
    elif not selected:
        answer = "Nessuna tavola disponibile per questa richiesta nel catalogo."
    else:
        answer = "\n".join(f"{c['comic_id']} — {c['title']} | diritti: {c.get('rights_status', 'TO_VERIFY')} | NFT: {c.get('nft_status', 'NOT_SELECTED')}\n{c.get('public_url', '')}" for c in selected)
    return jsonify({"answer": answer, "source": "nicola-comics-catalog", "mode": "catalog_adapter",
                    "action": action, "sources": [public_entry(c) for c in selected],
                    "gallery_url": GALLERY_URL, "api_base_url": pilot_base_url() or None,
                    "notice": "NFT_CANDIDATE indica una proposta da valutare, non una prova di mint. Il collegamento al Zorgax pubblico resta da verificare."})


@comics_api.post("/api/zorgax/ask")
def zorgax_catalog():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Corpo JSON obbligatorio"}), 400
    return answer_catalog(data)
