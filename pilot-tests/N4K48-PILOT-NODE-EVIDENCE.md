# N4K48 Pilot Node — Local Test Evidence

Timestamp: 2026-10-03T12:57:21+02:00
Environment: Windows / Docker Desktop
Repository: myzubster-mvp
Branch: main
Base commit: 92b4bae8fc81ea163ffe63ddc8b7df4629674ed7
Working tree: MODIFIED (local development state)

## Automated test

Result: PASS
Passed: 7
Failed: 0

Verified:
- Docker MVP API running and healthy
- Comics catalog available (3 items)
- N4K48 NFT candidate query
- Comic detail query
- Zorgax next_steps
- Forbidden action rejected with HTTP 400
- Local ledger readable (3 test events)

## Persistence

Docker volume:
myzubster-mvp_observations-data

Mount destination:
/data

API restart test:
PASS — API returned healthy and the same 3 local test ledger events remained available.

## Test script integrity

SHA-256:
C3A8C2830BB539CEA1BDD2A0C3B63C820E20D123A8521AC7BF63896F7F84F920

## Git working tree

 M docker-compose.yml
 M index.html
 M src/api/server.py
 M src/core/economics.py
 M tests/test_economics.py
?? pilot-tests/

## Evidence boundaries

- Ledger events are local test data.
- No real revenue/payment is claimed.
- NFT_CANDIDATE does not mean an NFT was minted.
- No authenticated Node Bridge test was performed.
- No BRIDGE_NODE_TOKEN was used.
- No new Internet-facing local service was exposed.
- No onion configuration was modified.
- Node Bridge remains blocked pending identification of the exact connector source/version.

