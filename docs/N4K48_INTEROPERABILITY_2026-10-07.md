# N4K48 live interoperability checkpoint — 2026-10-07

## Status

**TESTED / PASS** for the bounded technical interoperability path documented below.

On 7 October 2026 a controlled live `gallery` request crossed the deployed MyZubster Node Bridge and the contributor-controlled N4K48 Docker environment successfully.

## Tested path

```text
MyZubster VPS
    ↓
authenticated HTTPS broker
    ↓
contributor-controlled N4K48 Docker agent
    ↓
local MyZubster comics catalog
    ↓
result returned to Bridge
```

## Observed result

- broker job accepted successfully;
- the N4K48 agent processed the request from the contributor-controlled environment;
- the result returned to the broker with `state: done`;
- four catalog titles were returned:
  1. Dall’idea software al metaverso
  2. Il software prende forma
  3. Verso Neon Plaza
  4. Il ponte da costruire
- repeated reads returned the same completed result during the job TTL;
- after TTL expiry the broker returned `{"error":"expired"}`.

## Immutable/runtime references

- N4K48 agent SHA-256: `75ab34d21f668fa48383ac7070c717b074c868694c3042928e4532b5ccd34fa1`
- upstream PR head recorded at checkpoint: `0be7a6e38d8266d1b29ac6367ad345c65a2d2490`
- deployed broker image recorded upstream: `sha256:8b12286214237c650d8f54edb96a49e635a70e8b9db87e47aec3ea912683a6c1`
- deployed `broker.py` SHA-256 recorded upstream: `57deb663ceb990c8ddd709f04ae646dd0dd87ff3fb33bbdfa0d28be0bddafca6`

## Public upstream evidence

MyZubster PR #1545, maintainer checkpoint:

https://github.com/MyZubster-Ecosystem/myzubster/pull/1545#issuecomment-6041485188

## Evidence boundary

This checkpoint demonstrates tested interoperability between independently administered environments over the authenticated broker path.

It does **not** establish complete decentralization, direct peer-to-peer networking, production readiness, security certification, or broader scientific/clinical validation. The broker/VPS remains part of this tested path.

No credentials, tokens, private keys or secret values are included in this evidence record.
