# MyZubster MVP / N4K48 — Development Roadmap

Updated: 18 September 2026

This roadmap tracks the path from the verified local AI/RAG foundation to a publicly verified Zorgax integration and, only after evidence is available, NFT/Marketplace readiness.

- Repository: https://github.com/nicolaususnicola-lgtm/myzubster-mvp
- RAG implementation: https://github.com/nicolaususnicola-lgtm/myzubster-mvp/commit/8da7435ddc1b9ae8b2f5c2eea5debd2df4bc5f47
- Linear roadmap: https://linear.app/n4k48/project/myzubster-mvp-n4k48-roadmap-f38d28c6a077

## Guiding rule — Evidence first

A feature or state is considered verified only when supported by reproducible technical or documentary evidence. Narrative concepts, candidate states and planned integrations are not treated as completed functionality.

## Phase 1 — Local AI / RAG Foundation

- [x] Run Ollama, Qdrant, API and Open WebUI locally.
- [x] Use `nomic-embed-text` for embeddings and Mistral for generation.
- [x] Separate observation indexing from retrieval.
- [x] Persist new observations before AI indexing.
- [x] Query Qdrant without re-indexing every observation on every question.
- [x] Add the versioned Markdown knowledge base.
- [x] Add `scripts/ingest_knowledge.py` with deterministic point IDs.
- [x] Verify local tests: **25/25 passed**.
- [x] Verify ingestion: **38 knowledge chunks + 4 observations = 42 Qdrant points**.

Linear: **N4K-13, N4K-14**

## Phase 2 — Retrieval & Performance

- [ ] Improve Zorgax-specific retrieval so relevant `knowledge/ZORGAX.md` context ranks better.
- [ ] Evaluate chunking, metadata/filtering and ranking.
- [ ] Profile Ollama prompt/token processing.
- [ ] Reduce RAG latency; the observed Zorgax status query completed in about **80.75 s**.
- [ ] Tune context size and generation limits based on measurements rather than hiding latency with larger timeouts.

Linear: **N4K-15, N4K-16**

## Phase 3 — Zorgax Integration

- [ ] Validate the read-only Nicola Comics/Zorgax adapter configuration.
- [ ] Keep `gallery`, `detail`, `candidate` and `next_steps` covered by tests.
- [ ] Prepare a reachable HTTPS pilot.
- [ ] Configure `NICOLA_COMICS_BASE_URL` in the hosting environment.
- [ ] Keep authentication secrets outside Git.
- [ ] Do not expose the local development PC as the public endpoint.

Linear: **N4K-17, N4K-18**

## Phase 4 — Public E2E Verification

The public Zorgax connection is **not yet considered end-to-end verified**.

Target flow:

1. Request Nicola Comics through the public Zorgax path.
2. Retrieve the gallery.
3. Open a comic detail/card.
4. Verify the public image.
5. Retrieve the NFT candidate state.
6. Display and verify `rights_status` and on-chain status.
7. Record test date, environment and reproducible evidence.

- [ ] Complete the public end-to-end test.
- [ ] Record evidence before marking the integration complete.

Linear: **N4K-19**

## Phase 5 — Evidence / NFT / Marketplace Readiness

Current boundary: `n4k48-comic-001` remains **NFT_CANDIDATE / PROPOSED_FOR_REVIEW**. Rights remain **TO_VERIFY**. This roadmap does not claim an NFT has been minted.

- [ ] Document rights and provenance for the candidate.
- [ ] Confirm final selection only after rights verification.
- [ ] If minting is requested, require verifiable chain/network, contract address, token ID and transaction hash.
- [ ] Never mark an item `MINTED` without those proofs.
- [ ] Evaluate the Marketplace path only after required evidence is validated.

Linear: **N4K-20, N4K-21, N4K-22**

## Architecture

```text
Knowledge / Observations
        |
        v
nomic-embed-text
        |
        v
      Qdrant
        |
        v
Retrieval / Context
        |
        v
 Ollama + Mistral
        |
        v
Grounded AI response + sources
```

Write path:

```text
create observation -> persist -> embed -> index in Qdrant
```

Question path:

```text
question -> embed -> Qdrant search -> context -> Mistral -> answer
```

## Definition of progress

- **Done** — backed by current local evidence or committed implementation.
- **Todo** — defined next work with no completion claim.
- **Backlog** — later work dependent on earlier verification.

The objective is to evolve MyZubster/N4K48 from a functioning local RAG prototype into a reproducible public integration without confusing planned functionality with verified functionality.
