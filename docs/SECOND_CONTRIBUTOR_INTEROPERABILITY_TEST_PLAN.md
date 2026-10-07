# Second contributor interoperability test — plan

Status: **PROPOSED / CONSENT-GATED**

## Objective

Demonstrate that the N4K48 interoperability model is not specific to the Nicola ↔ Daniel pairing by reproducing a bounded, sanitized interoperability checkpoint with a second independently administered contributor environment.

## Candidate selection

Public MyZubster coordination currently provides stronger technical evidence for:

1. **@khongten124** — contributor-side interoperability already documented as TESTED in the Open Period Care/read-only evidence path.
2. **@Shweta-singh24** — documented technical/verifier path; independent verifier run remains an explicit next checkpoint.
3. **@foxxx009** — invited/proposed contributor connection, but no N4K48 Bridge opt-in or independently administered node capability is assumed by this plan.

No contributor is enrolled or assigned by this document. A direct N4K48 connection proceeds only after explicit opt-in and Nicola's approval.

## Proposed bounded test

```text
N4K48 / Nicola environment
        ↓
versioned/sanitized interoperability fixture
        ↓
MyZubster Bridge or agreed read-only exchange boundary
        ↓
second contributor-controlled environment
        ↓
deterministic result + evidence hash
```

The first reproduction should avoid production secrets and should not require direct VPS access.

## Preconditions

- contributor explicitly opts in;
- exact public repository, branch and commit are recorded;
- test objective and expected output are agreed;
- protocol/fixture version is frozen;
- only synthetic or explicitly authorized non-sensitive data are used;
- no passwords, tokens, SSH private keys, wallet seeds or private endpoints are published;
- rollback/stop procedure is documented.

## Minimum fixture

The shared fixture should contain:

- protocol identifier/version;
- unique test/job identifier;
- bounded action;
- deterministic input;
- expected normalized output;
- evidence/provenance metadata;
- content hash;
- explicit expiry/TTL where applicable.

## PASS criteria

A checkpoint is **TESTED / PASS** only if:

1. the second environment is independently administered;
2. the exact fixture/version is recorded;
3. the second environment processes or verifies the agreed input without sharing N4K48 filesystem/database privileges;
4. actual output matches the agreed normalized result;
5. evidence/provenance can be independently checked;
6. logs/output are sanitized;
7. failure/limitations are recorded;
8. public evidence links exact repo/commit and date.

## Non-claims

PASS would demonstrate reproducible contributor-to-contributor interoperability for the exact tested path. It would not by itself establish direct P2P networking, full decentralization, production readiness, security certification, partnership or payment.

## Public coordination

Canonical MyZubster coordination issue:

https://github.com/MyZubster-Ecosystem/myzubster/issues/1520

Existing pilot-node network issue:

https://github.com/MyZubster-Ecosystem/myzubster/issues/1505

The next action is to obtain explicit contributor opt-in before selecting the second environment and freezing the exact test fixture.
