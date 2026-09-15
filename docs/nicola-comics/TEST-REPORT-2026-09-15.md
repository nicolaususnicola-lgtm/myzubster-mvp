# Nicola Comics × MyZubster — report test locale

Data: 15 settembre 2026

## Scopo

Registrare in modo riproducibile la verifica locale del catalogo Nicola Comics e dell'adapter in sola lettura destinato all'integrazione con Zorgax.

## Ambiente e avvio

Il repository è stato aggiornato sul PC di Nicola e il servizio è stato ricostruito e avviato tramite Docker Compose:

```text
docker compose up --build -d
```

Questo report documenta il test locale; non dichiara una distribuzione sul Zorgax pubblico.

## Risultati verificati

- `GET /api/comics` restituisce le tre tavole N4K48 del pilot (`count: 3`).
- `POST /api/zorgax/ask` con domanda `Mostrami i fumetti di Nicola` e azione `gallery` restituisce titoli, link alle immagini e stato delle schede.
- La tavola `n4k48-comic-001` / **Dall'idea software al metaverso** risulta `NFT_CANDIDATE` / `PROPOSED_FOR_REVIEW`.
- Le altre due tavole non sono selezionate come candidate.
- Lo stato dei diritti resta `TO_VERIFY`.
- I campi di prova on-chain restano vuoti: nessun mint è dichiarato o eseguito dal pilot.
- L'adapter è in sola lettura e usa azioni esplicite; non interpreta autonomamente qualsiasi domanda in linguaggio naturale.

## Flusso end-to-end da verificare sul servizio pubblico

1. Richiesta dei fumetti di Nicola.
2. Apertura della scheda di una tavola.
3. Apertura dell'immagine pubblicata.
4. Richiesta della candidata NFT.
5. Visualizzazione dello stato dei diritti e delle prove on-chain.

## Stato del test

**Locale: PASS.** Il catalogo e l'adapter rispondono come previsto nell'ambiente locale verificato da Nicola.

**Zorgax pubblico: PENDING.** Serve concordare con il responsabile del servizio:

- dove ospitare un endpoint raggiungibile;
- come autorizzare le chiamate dal Zorgax pubblico;
- come mappare le intenzioni dell'utente alle azioni `gallery`, `detail`, `candidate`, `next_steps`;
- data e ambiente della prova end-to-end.

## Diritti e NFT

La tavola 01 resta una **candidata proposta**, non un NFT mintato. Prima di una selezione finale o di qualunque mint vanno documentate provenienza e autorizzazioni degli elementi visivi per l'uso previsto. Nessuna seed phrase, chiave privata, wallet operation, pagamento o funzione di mint è esposta dall'adapter.

## Riferimenti

- `docs/nicola-comics/ZORGAX.md` — contratto e istruzioni dell'adapter.
- `docs/nicola-comics/GALLERY.md` — galleria e schede.
- `docs/nicola-comics/comics.manifest.json` — catalogo versionato.
- `docs/n4k48-comics/ROADMAP.md` — avanzamento operativo.

## Prossima decisione richiesta

Individuare il responsabile del Zorgax pubblico e concordare hosting + autorizzazione dell'endpoint. Solo dopo questo passaggio il pilot può essere verificato end-to-end fuori dall'ambiente locale.
