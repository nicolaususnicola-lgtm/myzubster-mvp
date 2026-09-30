# MyZubster Knowledge Card — Sepolia Proof v2

## Purpose

This proof anchors a SHA-256 digest derived from a canonical representation of the **content** of the MyZubster Knowledge Card:

- Card: `Prove Docker e chat AI del progetto myzubster-mvp`
- Card ID: `6abaaefb3a7460c4574a45fd`
- Public card: https://www.myzubster.com/knowledge-card?id=6abaaefb3a7460c4574a45fd
- Canonical payload: `proofs/knowledge-card-6abaaefb3a7460c4574a45fd-v1.json`

This differs from proof v1, which anchored the SHA-256 of the Knowledge Card URL string rather than the card content.

## Canonical representation

Format identifier: `MYZUBSTER-KNOWLEDGE-CARD-V1`

The canonical payload is stored in the repository so that the digest can be independently recomputed. The proof refers to those exact UTF-8 bytes as committed; changing any byte produces a different digest.

## SHA-256

Canonical payload SHA-256:

```
6097e05866bafceec24663d2638cb1dae5742ac78284abbfd45cc9c3b0bfb845
```

Solidity `bytes32` value:

```
0x6097e05866bafceec24663d2638cb1dae5742ac78284abbfd45cc9c3b0bfb845
```

## Ethereum Sepolia attestation

Contract: `MyZubsterProof`

Contract address:

```
0x21787249Df054132093FcF09bB914C0CCC539390
```

Deployment transaction:

```
0xc837ba3f3046f3712e3eba4b81107cb22939b61300f2cab3cfe5bbb7b3319ded
```

Network: Ethereum Sepolia (`chainId 11155111`)

Contract:
https://sepolia.etherscan.io/address/0x21787249Df054132093FcF09bB914C0CCC539390

Deployment transaction:
https://sepolia.etherscan.io/tx/0xc837ba3f3046f3712e3eba4b81107cb22939b61300f2cab3cfe5bbb7b3319ded

## On-chain verification

Calling `knowledgeHash()` on the deployed contract returned:

```
0x6097e05866bafceec24663d2638cb1dae5742ac78284abbfd45cc9c3b0bfb845
```

This exactly matches the SHA-256 value documented above.

The contract is intentionally immutable for this proof: `knowledgeHash` is assigned in the constructor and the contract exposes no public write function.

## Reproduce the digest

From the repository root:

```bash
sha256sum proofs/knowledge-card-6abaaefb3a7460c4574a45fd-v1.json
```

Expected result:

```
6097e05866bafceec24663d2638cb1dae5742ac78284abbfd45cc9c3b0bfb845
```

Python alternative:

```bash
python -c "import hashlib, pathlib; p=pathlib.Path('proofs/knowledge-card-6abaaefb3a7460c4574a45fd-v1.json'); print(hashlib.sha256(p.read_bytes()).hexdigest())"
```

## What this proof establishes

The Sepolia contract records a digest equal to the SHA-256 of the exact canonical payload committed in this repository. Anyone can recompute the digest from that file and compare it with `knowledgeHash()` on Sepolia.

It does **not** independently certify the truth, ownership, or professional validity of the statements contained in the Knowledge Card. It establishes a cryptographic link between the committed canonical payload and the on-chain digest.


## N4K48 profile evidence update — 2026-09-30

The N4K48 GitHub profile was updated after completing the repeatable Proof v2 verifier (MYZ-213) to expose the latest documented knowledge path:

`N4K48 → Knowledge Card → GitHub evidence → canonical payload → SHA-256 → Ethereum Sepolia Proof v2 → Knowledge Graph`

Profile evidence commit: [b98230ceab71a760c8045f0c42401e0c70b12a1c](https://github.com/nicolaususnicola-lgtm/nicolaususnicola-lgtm/commit/b98230ceab71a760c8045f0c42401e0c70b12a1c)

Verifier implementation: [merged PR #16](https://github.com/nicolaususnicola-lgtm/myzubster-mvp/pull/16)

This profile update is supporting evidence of the documented learning/contribution path. It does not change the immutable Proof v2 payload or its on-chain digest.
