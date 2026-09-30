# MyZubster Knowledge Proof v3 — Ethereum Sepolia

## Purpose

This document records the third MyZubster Knowledge Card proof for card `6abaaefb3a7460c4574a45fd`.

The proof anchors the SHA-256 digest of the exact committed bytes of:

`proofs/knowledge-card-6abaaefb3a7460c4574a45fd-v3.json`

It establishes a reproducible cryptographic link between that immutable payload and the value stored on Ethereum Sepolia. It does **not** automatically certify the truth of the claims, ownership, identity, or professional competence.

## Canonical payload

- Knowledge Card ID: `6abaaefb3a7460c4574a45fd`
- Payload file: `proofs/knowledge-card-6abaaefb3a7460c4574a45fd-v3.json`
- Final payload commit: `e57261a325625057350aa059ca142f1eb84b30c2`
- Exact size verified locally: `5083` bytes
- SHA-256:

```text
d1c89d2a4157a159b56e92825ca59fdb1f0e84e003b05e022af67da69ed25ac4
```

The digest was independently reproduced locally with both `sha256sum` and Python `hashlib.sha256(data)` over `Path.read_bytes()`.

## Sepolia attestation

- Network: Ethereum Sepolia
- chainId: `11155111`
- Contract: `0x3233fA7f8c50Aa25d9B1263c25F28535B6eA59bF`
- Deploy transaction: `0x5c7717be6dc70e6416f8053c72bb1e2bec2b7c5462b23fcb9c4b1077f907fed4`
- Block: `11817050`
- Deployer: `0x08ae56e99AdB11Df571c437B18620D6c0075d700`
- Receipt status: `1 (success)`

Public references:

- Contract: https://sepolia.etherscan.io/address/0x3233fA7f8c50Aa25d9B1263c25F28535B6eA59bF
- Transaction: https://sepolia.etherscan.io/tx/0x5c7717be6dc70e6416f8053c72bb1e2bec2b7c5462b23fcb9c4b1077f907fed4

## Independent on-chain readback

The public read-only call:

```bash
cast call 0x3233fA7f8c50Aa25d9B1263c25F28535B6eA59bF "knowledgeHash()(bytes32)" \
  --rpc-url https://ethereum-sepolia-rpc.publicnode.com
```

returned:

```text
0xd1c89d2a4157a159b56e92825ca59fdb1f0e84e003b05e022af67da69ed25ac4
```

This exactly matches the SHA-256 of the 5083-byte committed v3 payload.

The deployment receipt was also read through the public Sepolia RPC and reported the contract address above, block `11817050`, deployer above, and `status 1 (success)`.

## Reproduce the payload digest

```bash
sha256sum proofs/knowledge-card-6abaaefb3a7460c4574a45fd-v3.json
wc -c proofs/knowledge-card-6abaaefb3a7460c4574a45fd-v3.json
```

Expected:

```text
d1c89d2a4157a159b56e92825ca59fdb1f0e84e003b05e022af67da69ed25ac4
5083 bytes
```

## Verify with the MYZ-213 CLI

From the repository root, run the script as a module-path-aware command:

```bash
PYTHONPATH=. python3 scripts/verify_knowledge_proof.py \
  proofs/knowledge-card-6abaaefb3a7460c4574a45fd-v3.json \
  0x3233fA7f8c50Aa25d9B1263c25F28535B6eA59bF \
  --expected-hash 0xd1c89d2a4157a159b56e92825ca59fdb1f0e84e003b05e022af67da69ed25ac4
```

The plain invocation `python3 scripts/verify_knowledge_proof.py ...` can fail in some environments with `ModuleNotFoundError: No module named 'src'` because Python places the `scripts/` directory, rather than the repository root, first on the import path. Setting `PYTHONPATH=.` from the repository root resolves that invocation issue without changing the proof data.

## Verification boundary

A `MATCH` means the exact payload bytes hash to the same bytes32 value returned by the proof contract. This supports integrity and provenance of the documented artifact. It does not by itself prove that every statement in the Knowledge Card is true, that an identity owns every referenced artifact, or that professional skills have been independently certified.

Proof v3 is immutable evidence for this specific payload version. Later changes to the live Knowledge Card are not retroactively included in this digest.
