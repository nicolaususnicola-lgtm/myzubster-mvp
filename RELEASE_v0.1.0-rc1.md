# MyZubster MVP v0.1.0-rc1

**Release class:** public release candidate  
**Distribution:** source code + Docker  
**Production status:** experimental MVP; not production-ready  
**Prepared:** 2026-10-03

## What users can run

This release candidate packages the current tested checkpoint as a reproducible public Docker application.

Included capabilities:

- MyZubster observation API and persistent JSON storage;
- internal MYZ ledger and derived balances;
- revenue/cost scenario simulator;
- local AI/RAG integration with Ollama + Qdrant;
- Nicola Comics catalog and read-only Zorgax adapter;
- public comic evidence links and candidate status;
- knowledge-proof verification utilities documented by the project.

The public Nicola Comics pilot is separately deployed at https://myzubster-mvp.onrender.com/ . A public pilot deployment does not mean every local feature or dependency is production-ready.

## Download / install

### Option A — source archive

GitHub can provide ZIP/tar source archives for the release branch/commit. After extracting:

    docker compose up --build -d
    docker compose ps

The local API is bound to `http://127.0.0.1:5000`.

### Option B — Git clone

    git clone https://github.com/nicolaususnicola-lgtm/myzubster-mvp.git
    cd myzubster-mvp
    git checkout release/v0.1.0-rc1
    docker compose up --build -d

## Requirements

Minimum practical requirements: Docker with Docker Compose support; Git only when cloning. Optional AI/RAG additionally expects Ollama and the models documented in the README (`qwen2.5:0.5b` and `nomic-embed-text`). Qdrant and Open WebUI are Compose services.

## Security / configuration boundary

- Do not commit `.env`, private keys, PEM files, tokens, passwords, wallet secrets, or API secrets.
- The repository `.gitignore` excludes common local secret files.
- Docker services are bound to loopback by default in the provided Compose file.
- Public internet deployment requires appropriate hosting/reverse proxy, HTTPS, access controls where needed, persistent storage, backups, and secret management.
- Do not expose the development Compose stack directly to the public internet.

## Verification before calling this stable

The repository contains automated Python/API/Docker checks and a public Nicola Comics verification script. This document does not claim a fresh CI pass for this release branch until a workflow run provides that evidence.

Before promoting from `v0.1.0-rc1` to stable:

1. run the automated test suite on the exact release commit;
2. build and health-check the Docker image from that commit;
3. verify the public pilot endpoints;
4. perform a clean-machine Docker installation test;
5. review dependency/security findings;
6. confirm documentation and licensing for distributed assets;
7. decide whether distribution remains source/Docker-only or also needs a native desktop installer.

## Not included

This release candidate does **not** claim a Windows/macOS native installer, signed desktop application, production SLA, active wallet/payout functionality, real payment settlement, verified NFT mint, or verified commercial/NFT rights for assets marked `TO_VERIFY`.

## Nicola Comics boundary

For `n4k48-comic-001` the state remains `rights_status: TO_VERIFY`, `nft_status: NFT_CANDIDATE`, `selection_status: PROPOSED_FOR_REVIEW`, with on-chain fields empty/null. Software distribution does not change or grant asset/content rights.

## License

The repository currently contains an MIT license. Distribution must also respect any separate rights or restrictions applicable to third-party or project visual/content assets.