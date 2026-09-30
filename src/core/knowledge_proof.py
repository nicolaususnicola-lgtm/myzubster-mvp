"""Cryptographic verification helpers for MyZubster Knowledge Card proofs.

The verifier hashes exact payload bytes and compares them with Sepolia storage.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import requests


SEPOLIA_CHAIN_ID = 11155111
DEFAULT_SEPOLIA_RPC_URL = "https://ethereum-sepolia-rpc.publicnode.com"
KNOWLEDGE_HASH_SIGNATURE = "knowledgeHash()"


def sha256_file(path: str | Path) -> str:
    """Return the SHA-256 hex digest of the exact file bytes."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_bytes32(value: str) -> str:
    if not isinstance(value, str):
        raise ValueError("bytes32 value must be a string")
    normalized = value.strip().lower()
    if not normalized.startswith("0x"):
        normalized = "0x" + normalized
    if len(normalized) != 66:
        raise ValueError("bytes32 value must contain exactly 32 bytes")
    try:
        int(normalized[2:], 16)
    except ValueError as error:
        raise ValueError("bytes32 value is not valid hexadecimal") from error
    return normalized


def read_knowledge_hash(
    contract_address: str,
    *,
    rpc_url: str = DEFAULT_SEPOLIA_RPC_URL,
    timeout: float = 20,
) -> str:
    """Read knowledgeHash from storage slot 0 of MyZubsterProof."""
    if not isinstance(contract_address, str) or not contract_address.startswith("0x") or len(contract_address) != 42:
        raise ValueError("invalid Ethereum contract address")

    signature_hex = "0x" + KNOWLEDGE_HASH_SIGNATURE.encode("utf-8").hex()
    selector_response = requests.post(
        rpc_url,
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "web3_sha3",
            "params": [signature_hex],
        },
        timeout=timeout,
    )
    selector_response.raise_for_status()
    selector_payload: dict[str, Any] = selector_response.json()
    if selector_payload.get("error"):
        raise ValueError(f"Ethereum RPC error: {selector_payload['error']}")
    selector_hash = selector_payload.get("result", "")
    if not isinstance(selector_hash, str) or len(selector_hash) < 10:
        raise ValueError("Ethereum RPC returned an invalid function signature hash")
    selector = selector_hash[:10]

    response = requests.post(
        rpc_url,
        json={
            "jsonrpc": "2.0",
            "id": 2,
            "method": "eth_call",
            "params": [
                {"to": contract_address, "data": selector},
                "latest",
            ],
        },
        timeout=timeout,
    )
    response.raise_for_status()
    payload: dict[str, Any] = response.json()
    if payload.get("error"):
        raise ValueError(f"Ethereum RPC error: {payload['error']}")
    return normalize_bytes32(payload.get("result", ""))


def verify_knowledge_proof(
    payload_path: str | Path,
    contract_address: str,
    *,
    expected_hash: str | None = None,
    rpc_url: str = DEFAULT_SEPOLIA_RPC_URL,
    timeout: float = 20,
) -> dict[str, Any]:
    """Compare exact payload bytes with the bytes32 stored on Sepolia."""
    digest = sha256_file(payload_path)
    calculated = normalize_bytes32(digest)
    onchain = read_knowledge_hash(contract_address, rpc_url=rpc_url, timeout=timeout)
    expected = normalize_bytes32(expected_hash) if expected_hash else None

    return {
        "status": "MATCH" if calculated == onchain and (expected is None or calculated == expected) else "NO_MATCH",
        "payload_sha256": digest,
        "calculated_bytes32": calculated,
        "onchain_bytes32": onchain,
        "expected_bytes32": expected,
        "payload_matches_onchain": calculated == onchain,
        "payload_matches_expected": expected is None or calculated == expected,
        "network": "Ethereum Sepolia",
        "chain_id": SEPOLIA_CHAIN_ID,
        "contract_address": contract_address,
    }
