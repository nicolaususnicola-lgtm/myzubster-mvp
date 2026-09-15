# Nicola Comics × MyZubster

Status: `PROTOTYPE`

This folder starts the Nicola Comics pilot in the `nicolaususnicola-lgtm/myzubster-mvp` fork.

## Objective

Build a small software pilot that connects Nicola's comics to MyZubster, Zorgax, NFT proof, and later Marketplace integration.

## Target flow

**Nicola → profile → comics gallery → NFT candidate → verified NFT proof → Zorgax → Marketplace**

## Pilot milestones

1. Define project name, theme, characters, and series format.
2. Create Nicola profile metadata.
3. Publish at least 3 comic entries in a gallery manifest.
4. Select 1 comic as `NFT CANDIDATE`.
5. Record provenance/hash and, only after a real mint, contract address + token ID + transaction hash.
6. Connect the project to Zorgax so the user can ask to see Nicola's comics.
7. Test the complete path with Nicola.

## Guardrails

- Do not store seed phrases or private keys.
- Do not mark an artwork `MINTED` without verifiable on-chain evidence.
- Keep rights/authorship explicit.
- Keep NFT proof separate from ordinary Marketplace monetization.

## Coordination

- GitHub issue: https://github.com/MyZubster-Ecosystem/myzubster/issues/1052
- Linear: MYZ-142

## Avanzamento — 15 settembre 2026

Tre nuove tavole N4K48 sono registrate nel catalogo, con provenienza AI dichiarata e hash dei file pubblicati. La prima è candidata proposta, comunicata a Daniel il 9 settembre; selezione finale, diritti e mint restano da verificare.

- [Galleria e schede](GALLERY.md)
- [Manifest del catalogo](comics.manifest.json)
- [Roadmap operativa](https://github.com/nicolaususnicola-lgtm/myzubster-mvp/blob/main/docs/n4k48-comics/ROADMAP.md)

Il catalogo è documentale. L’integrazione runtime con Zorgax e Marketplace non è ancora verificata.
