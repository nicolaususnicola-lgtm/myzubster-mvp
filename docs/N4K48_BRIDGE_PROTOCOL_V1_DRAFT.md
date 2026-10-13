# N4K48 ↔ MyZubster Bridge Protocol v1 — Draft

Status: **DRAFT FOR JOINT REVIEW**  
Baseline: live interoperability checkpoint **TESTED / PASS — 2026-10-07**

This document proposes a versioned contract between the contributor-controlled N4K48 agent and the MyZubster Ecosystem Bridge. It freezes the behavior demonstrated by the 2026-10-07 checkpoint as the starting compatibility baseline, while leaving room for joint review before declaring v1 stable.

## 1. Scope

v1 covers the bounded path:

```text
MyZubster VPS → authenticated HTTPS Bridge → N4K48 agent
              → local catalog → result returned to Bridge
```

It specifies protocol versioning, job/lease identity, actions, results, errors, TTL behavior, capabilities and security boundaries. It does not define direct P2P networking or claim complete decentralization.

## 2. Versioning

Proposed protocol identifier:

```text
n4k48-bridge/1.0
```

Rules:

- compatible additive changes may remain within `1.x`;
- removing/renaming required fields or changing their meaning requires a new major version;
- both sides should reject unsupported major versions explicitly;
- the protocol version should be carried in jobs/results once both implementations support the field.

Until Daniel/MyZubster confirms the exact wire field, `protocol_version` below is **proposed**, not asserted as part of the already deployed broker.

## 3. Job envelope

Proposed normalized representation:

```json
{
  "protocol_version": "n4k48-bridge/1.0",
  "job_id": "<opaque unique id>",
  "lease_id": "<opaque lease id>",
  "action": "gallery",
  "payload": {},
  "expires_at": "<timestamp or equivalent TTL metadata>"
}
```

Required semantics:

- `job_id` identifies one logical job;
- `lease_id` identifies the current authorization to process that job;
- `action` selects a supported operation;
- expiry/TTL prevents stale work from remaining valid indefinitely;
- unknown actions or malformed identifiers must fail safely.

Exact deployed field names must be confirmed against the Bridge implementation before v1 is marked stable.

## 4. Actions and capabilities

The verified baseline action is:

```text
gallery
```

A future capability exchange should allow a node to advertise:

```json
{
  "protocol_versions": ["n4k48-bridge/1.0"],
  "actions": ["gallery"]
}
```

The Bridge should not intentionally assign a node an action/version it has not advertised as supported.

## 5. Result envelope

Proposed normalized successful result:

```json
{
  "protocol_version": "n4k48-bridge/1.0",
  "job_id": "<job id>",
  "lease_id": "<lease id>",
  "state": "done",
  "result": {
    "action": "gallery",
    "items": []
  },
  "evidence": []
}
```

Required semantics:

- result must correspond to the current `job_id` and `lease_id`;
- `state: done` means processing completed successfully;
- catalog data must be validated before submission;
- generated content must not silently replace authoritative evidence;
- evidence/provenance fields will be refined under the joint evidence-envelope milestone.

The 2026-10-07 live checkpoint verified a completed `gallery` result returning four catalog titles.

## 6. Lease and TTL semantics

v1 should preserve these observed properties:

- work is processed only while its lease/job is valid;
- stale or expired work is not treated as a current successful result;
- completed results may remain readable during their configured TTL;
- after TTL expiry the tested Bridge returned `{"error":"expired"}`;
- repeated reads during the result TTL must not mutate the completed result.

To finalize v1, both sides must agree on lease duration, renewal (if any), reassignment behavior and treatment of late/duplicate results.

## 7. Error model

Proposed stable error codes:

| Code | Meaning |
| --- | --- |
| `invalid_request` | malformed or missing required data |
| `unsupported_protocol` | unsupported protocol major/version |
| `unsupported_action` | node does not support requested action |
| `unauthorized` | authentication/authorization failed |
| `expired` | job/result/lease no longer valid |
| `invalid_source_response` | local authoritative source failed validation |
| `temporary_failure` | retryable processing/network failure |
| `internal_failure` | bounded non-sensitive internal failure |

Error responses must not expose credentials, tokens, private keys or sensitive environment values.

Exact mapping to current Bridge HTTP/status behavior remains a joint decision.

## 8. Security boundary

v1 requires:

- HTTPS for non-loopback Bridge communication;
- node authentication;
- credentials supplied outside repository content and job/result payloads;
- no secret values in evidence, logs, screenshots or shared test output;
- bounded request timeouts and validation of remote/local responses;
- explicit credential rotation and revocation procedure.

The current credential mechanism is a tested bootstrap mechanism, not yet the final secret-lifecycle design.

## 9. Conformance

A v1 implementation should pass a shared fixture covering at minimum:

1. valid `gallery` job;
2. malformed job;
3. unsupported action;
4. invalid/stale lease;
5. local catalog/source failure;
6. duplicate/repeated result read;
7. result TTL expiry;
8. unsupported protocol version;
9. secret-redaction check.

N4K48 should be able to run these tests locally without production credentials. Daniel/MyZubster should provide a compatible Bridge fixture or safe non-production conformance path.

## 10. v1 acceptance gate

The draft becomes **STABLE v1** only when both sides agree on:

- exact wire field names and required/optional fields;
- version negotiation;
- lease duration/reassignment/late-result rules;
- canonical error codes and HTTP mapping;
- capability advertisement;
- shared conformance fixture;
- authentication/credential lifecycle boundary.

Until then, the status remains **DRAFT FOR JOINT REVIEW**.

## 11. Evidence baseline

N4K48 record:

https://github.com/nicolaususnicola-lgtm/myzubster-mvp/blob/main/docs/N4K48_INTEROPERABILITY_2026-10-07.md

Upstream MyZubster checkpoint:

https://github.com/MyZubster-Ecosystem/myzubster/pull/1545#issuecomment-6041485188

Verified N4K48 agent SHA-256:

`75ab34d21f668fa48383ac7070c717b074c868694c3042928e4532b5ccd34fa1`

This baseline proves bounded technical interoperability; it does not establish complete decentralization, direct P2P networking, production readiness or security certification.
