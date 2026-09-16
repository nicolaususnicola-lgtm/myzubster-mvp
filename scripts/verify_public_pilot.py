#!/usr/bin/env python3
"""Evidence-first smoke test for the public Nicola Comics × MyZubster pilot."""

import json
import os
import sys
from urllib.parse import urlparse

import requests

BASE_URL = os.getenv("NICOLA_COMICS_BASE_URL", "https://myzubster-mvp.onrender.com").rstrip("/")
TIMEOUT = float(os.getenv("NICOLA_COMICS_TEST_TIMEOUT", "30"))
EXPECTED_IDS = {"n4k48-comic-001", "n4k48-comic-002", "n4k48-comic-003"}


def fail(message):
    print(f"FAIL: {message}")
    raise AssertionError(message)


def check(condition, message):
    if not condition:
        fail(message)
    print(f"PASS: {message}")


def request_json(method, path, payload=None):
    url = f"{BASE_URL}{path}"
    response = requests.request(method, url, json=payload, timeout=TIMEOUT)
    check(response.status_code == 200, f"{method} {path} -> HTTP 200")
    try:
        return response.json()
    except ValueError as exc:
        fail(f"{method} {path} did not return JSON: {exc}")


def sources(data):
    value = data.get("sources", [])
    return value if isinstance(value, list) else []


def comic_id(item):
    return item.get("comic_id") or item.get("id")


def assert_evidence_boundary(item):
    check(item.get("rights_status") == "TO_VERIFY", "candidate rights_status remains TO_VERIFY")
    for key in ("contract_address", "token_id", "transaction_hash", "network", "metadata_uri"):
        check(item.get(key) in (None, ""), f"candidate {key} has no unverified on-chain claim")


def main():
    parsed = urlparse(BASE_URL)
    check(parsed.scheme == "https", "public base URL uses HTTPS")

    catalog = request_json("GET", "/api/comics")
    catalog_items = catalog.get("comics") or catalog.get("sources") or catalog.get("items") or []
    check(isinstance(catalog_items, list), "catalog response contains a list")
    ids = {comic_id(item) for item in catalog_items if isinstance(item, dict)}
    check(EXPECTED_IDS.issubset(ids), "catalog contains all three N4K48 pilot boards")

    gallery = request_json("POST", "/api/zorgax/ask", {
        "question": "Mostrami i fumetti di Nicola",
        "action": "gallery",
    })
    check(gallery.get("action") == "gallery", "gallery action is echoed correctly")
    gallery_ids = {comic_id(item) for item in sources(gallery) if isinstance(item, dict)}
    check(EXPECTED_IDS.issubset(gallery_ids), "gallery returns all three N4K48 boards")

    detail = request_json("POST", "/api/zorgax/ask", {
        "question": "Mostrami la scheda della tavola 01",
        "action": "detail",
        "comic_id": "n4k48-comic-001",
    })
    check(detail.get("action") == "detail", "detail action is echoed correctly")
    detail_items = sources(detail)
    check(any(comic_id(item) == "n4k48-comic-001" for item in detail_items if isinstance(item, dict)),
          "detail returns n4k48-comic-001")

    candidate = request_json("POST", "/api/zorgax/ask", {
        "question": "Quale candidata NFT?",
        "action": "candidate",
    })
    check(candidate.get("action") == "candidate", "candidate action is echoed correctly")
    candidate_items = [item for item in sources(candidate) if isinstance(item, dict)]
    check(len(candidate_items) == 1, "candidate returns exactly one proposed board")
    selected = candidate_items[0]
    check(comic_id(selected) == "n4k48-comic-001", "candidate is n4k48-comic-001")
    check(selected.get("nft_status") == "NFT_CANDIDATE", "candidate remains NFT_CANDIDATE")
    proposal = selected.get("selection_status") or selected.get("review_status") or selected.get("status")
    check(proposal == "PROPOSED_FOR_REVIEW", "candidate remains PROPOSED_FOR_REVIEW")
    assert_evidence_boundary(selected)

    next_steps = request_json("POST", "/api/zorgax/ask", {
        "question": "Quali sono i prossimi passi?",
        "action": "next_steps",
    })
    check(next_steps.get("action") == "next_steps", "next_steps action is echoed correctly")
    check(bool(next_steps.get("answer")), "next_steps returns an answer")

    print("\nPUBLIC PILOT VERIFICATION: PASS")
    print(json.dumps({"base_url": BASE_URL, "candidate": "n4k48-comic-001", "rights_status": "TO_VERIFY"}, indent=2))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (requests.RequestException, AssertionError) as exc:
        print(f"\nPUBLIC PILOT VERIFICATION: FAIL\n{exc}", file=sys.stderr)
        sys.exit(1)
