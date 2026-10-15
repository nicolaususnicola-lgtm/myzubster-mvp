# n4k48-comic-001 — Authorization record template

**Status:** `PENDING_AUTHORIZATION`  
**Prepared:** 2026-10-03  
**Comic ID:** `n4k48-comic-001`

This record is a template for an explicit, attributable authorization. It does **not** constitute authorization until the authorizing party completes or confirms the required fields through a verifiable reference.

## Asset covered

- **Title:** Dall’idea software al metaverso
- **Repository asset:** `docs/n4k48-comics/01-dall-idea-al-metaverso.png`
- **Publication commit:** `f853710e24c305cb292b271c0d37696147e35239`
- **Git blob SHA-1:** `bf90e43ba1c1524a5c955e6e0446fe774f83a2e7`
- **Immutable asset reference:** https://github.com/nicolaususnicola-lgtm/myzubster-mvp/blob/f853710e24c305cb292b271c0d37696147e35239/docs/n4k48-comics/01-dall-idea-al-metaverso.png

Authorization must identify this exact version or explicitly identify a different version.

## Authorizing party

To be completed/confirmed by the authorizing party:

- **Name / identity:** PENDING
- **Role / authority:** PENDING
- **Organization / project represented, if applicable:** PENDING
- **Verifiable identity/reference:** PENDING
- **Authorization date:** PENDING

The role must be sufficient for the scope being authorized. This template does not infer authority from repository access, commits, email participation, or project involvement.

## Scope matrix

Each scope must be answered independently.

| Intended use | Authorization | Conditions / limits |
| --- | --- | --- |
| Publication/display inside the Nicola Comics / MyZubster pilot | `PENDING` | PENDING |
| Public display through the Zorgax → Nicola Comics pilot | `PENDING` | PENDING |
| Promotional/non-commercial project communication | `PENDING` | PENDING |
| Commercial use | `PENDING` | PENDING |
| NFT selection / preparation | `PENDING` | PENDING |
| Mint / on-chain registration | `PENDING` | PENDING |

Allowed values should be explicit, for example `AUTHORIZED`, `NOT_AUTHORIZED`, or `NOT_APPLICABLE`; do not infer one scope from another.

## MyZubster-controlled elements

The authorizing party should state whether the asset contains names, logos, characters, visual assets, brand elements, or other material whose relevant rights are controlled by MyZubster or another party.

- **Controlled/external elements identified:** PENDING
- **Elements covered by this authorization:** PENDING
- **Elements excluded / requiring separate authorization:** PENDING

If another rights holder must authorize an element, keep the corresponding scope unresolved until that evidence is linked.

## Authorization statement

To become evidence, the authorizing party should provide an explicit statement substantially covering:

> I identify the exact asset/version above, state my role and authority, and explicitly authorize or decline each listed use. Any conditions or exclusions are stated in this record or in the linked verifiable reference.

A reply that only says “approved”, “looks good”, or approves the documentation/PR is **not** treated as rights authorization unless it explicitly covers the asset, role, scope, and limits.

## Verifiable evidence

At least one attributable reference must be linked:

- GitHub issue/PR comment by the authorizing identity: PENDING
- signed/attributable project record: PENDING
- attributable email confirmation archived/referenced by the project: PENDING
- other authoritative source: PENDING

**Evidence reference:** PENDING

## Status transition rule

Until the required authorization is explicit and verifiable:

- keep `rights_status: TO_VERIFY`;
- keep `nft_status: NFT_CANDIDATE`;
- keep `selection_status: PROPOSED_FOR_REVIEW`;
- keep network/contract/token/transaction/metadata fields empty.

After evidence is supplied, perform a new rights review. Authorization for pilot display does not automatically authorize commercial use, NFT selection, or minting.
