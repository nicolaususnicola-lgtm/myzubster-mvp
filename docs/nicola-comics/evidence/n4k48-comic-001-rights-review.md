# n4k48-comic-001 — Rights & provenance review

**Review date:** 2026-10-03  
**Comic ID:** `n4k48-comic-001`  
**Title:** Dall’idea software al metaverso  
**Current rights status:** `TO_VERIFY`  
**Current NFT status:** `NFT_CANDIDATE`  
**Selection status:** `PROPOSED_FOR_REVIEW`

## Purpose

This record freezes the evidence currently available for the first Nicola Comics candidate and defines the conditions required before changing its rights, selection, or on-chain status.

It is an evidence record, not a legal determination of copyright ownership or a mint authorization.

## Public provenance currently documented

- Creative contribution recorded in the pilot: Nicola / N4K48 — ideation and creative direction; image generated with AI assistance.
- Generation note: ImageGen, following Nicola’s instructions and using the already selected N4K48 character.
- Creation date recorded by the pilot: 2026-09-09.
- Published asset: `docs/n4k48-comics/01-dall-idea-al-metaverso.png`.
- Publication commit: `f853710e24c305cb292b271c0d37696147e35239`.
- Git blob SHA-1 recorded for the image: `bf90e43ba1c1524a5c955e6e0446fe774f83a2e7`.
- Candidate relationship: `CREATED_FOR_NICOLA_PILOT`.
- The candidate was proposed for review; proposal is not final selection, commercial authorization, or mint evidence.

### Evidence links

- Asset at immutable publication commit: https://github.com/nicolaususnicola-lgtm/myzubster-mvp/blob/f853710e24c305cb292b271c0d37696147e35239/docs/n4k48-comics/01-dall-idea-al-metaverso.png
- Pilot card: ../cards/n4k48-comic-001.md
- Versioned catalog: ../comics.manifest.json
- Gallery: ../GALLERY.md
- Pilot roadmap: ../../n4k48-comics/ROADMAP.md

## What is verified vs. not verified

| Claim | Current evidence | Status |
| --- | --- | --- |
| The published file is identified by a Git commit/blob | immutable commit + recorded blob SHA-1 | **DOCUMENTED** |
| Nicola/N4K48 provided ideation and creative direction | pilot provenance record | **DOCUMENTED AS PROJECT PROVENANCE** |
| AI assistance was used to generate the image | pilot generation record | **DOCUMENTED AS PROJECT PROVENANCE** |
| All visual elements are cleared for NFT/commercial use | no authoritative authorization attached to the pilot | **TO_VERIFY** |
| Use of any external MyZubster visual/brand elements is authorized for NFT/commercial use | no authoritative authorization attached to the pilot | **TO_VERIFY** |
| The work is finally selected for mint | current state is only `PROPOSED_FOR_REVIEW` | **NOT VERIFIED** |
| A mint/on-chain registration exists | network, contract, token ID and transaction hash are empty | **NOT VERIFIED** |

Git hashes establish file identity/provenance inside the repository; they do not establish legal ownership or licensing rights.

## Evidence required to move rights_status away from TO_VERIFY

Before changing `rights_status`, attach or reference authoritative evidence that covers the intended use. At minimum:

1. confirmation of the relevant rights holder(s) for the visual elements used;
2. confirmation that the intended publication/commercial/NFT use is permitted;
3. confirmation covering any MyZubster names, logos, characters, visual assets, or other externally controlled elements if present;
4. source/reference for each authorization, with date and scope;
5. unresolved restrictions recorded explicitly rather than inferred away.

A repository commit, email proposal, AI-generation note, or candidate label alone is insufficient to satisfy these requirements.

## Criteria for final selection

`selection_status` may move from `PROPOSED_FOR_REVIEW` to a final selected state only when:

- rights/provenance review is documented and no blocking authorization remains unresolved;
- the exact asset version to be selected is identified by immutable evidence;
- the pilot maintainer/authorized decision maker records the selection;
- the intended use and scope are stated;
- the catalog is updated without implying an on-chain state that has not occurred.

Selection and mint are separate events. Final selection must not populate blockchain fields.

## Criteria for any future on-chain status

Do not claim a mint or registration until independently inspectable evidence exists. A future on-chain record should identify, at minimum:

- network;
- contract address;
- token ID or equivalent identifier;
- transaction hash;
- metadata URI or canonical metadata reference where applicable;
- the exact selected asset/version;
- verification that the public transaction/contract data matches the catalog claim.

Until then, `network`, `contract_address`, `token_id`, `transaction_hash`, and `metadata_uri` remain empty/null.

## Current decision

**No status promotion is justified by the evidence currently attached to the pilot.**

Keep:

- `rights_status: TO_VERIFY`
- `nft_status: NFT_CANDIDATE`
- `selection_status: PROPOSED_FOR_REVIEW`
- all on-chain fields empty/null.

## Next evidence action

Obtain and attach the authoritative rights/authorization evidence for the intended use of `n4k48-comic-001`, including any applicable MyZubster-controlled visual or brand elements. After that evidence is available, repeat this review before changing catalog status.
