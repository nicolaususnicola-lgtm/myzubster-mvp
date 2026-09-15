# Nicola Comics × MyZubster — report test locale

Data: 15 settembre 2026

## Scopo

Registrare in modo riproducibile la verifica locale del catalogo Nicola Comics e dell'adapter in sola lettura destinato all'integrazione con Zorgax.

## Ambiente e avvio

Il repository è stato aggiornato sul PC di Nicola e il servizio è stato ricostruito e avviato tramite Docker Compose:

```text
docker compose up --build -d
```

Durante la verifica, `docker compose ps` ha mostrato il servizio API come `healthy` e raggiungibile su `localhost:5000`.

Questo report documenta il test locale; non dichiara una distribuzione sul Zorgax pubblico.

## Risultati verificati

- `GET /api/comics` restituisce le tre tavole N4K48 del pilot (`count: 3`).
- `POST /api/zorgax/ask` con azione `gallery` restituisce le tre tavole, titoli, link alle immagini e stato delle schede.
- `POST /api/zorgax/ask` con azione `detail` e `comic_id: n4k48-comic-001` restituisce correttamente la scheda della tavola 01.
- `POST /api/zorgax/ask` con azione `candidate` restituisce soltanto `n4k48-comic-001` / **Dall'idea software al metaverso**.
- La tavola 01 risulta `NFT_CANDIDATE` / `PROPOSED_FOR_REVIEW`.
- Le altre due tavole risultano `NOT_SELECTED`.
- Lo stato dei diritti resta `TO_VERIFY`.
- `transaction_hash`, `contract_address`, `token_id`, `network` e `metadata_uri` restano vuoti: nessun mint è dichiarato o eseguito dal pilot.
- `POST /api/zorgax/ask` con azione `next_steps` indica correttamente verifica di provenienza/autorizzazioni, conferma della candidata e futuro collegamento al Zorgax pubblico, specificando che il servizio non esegue mint.
- L'adapter è in sola lettura e usa azioni esplicite; non interpreta autonomamente qualsiasi domanda in linguaggio naturale.

## Nota sul test `candidate`

Una prima richiesta PowerShell con variabile `$body` ha restituito `400` / `Corpo JSON obbligatorio`. Ripetendo la stessa azione con JSON inline esplicito:

```text
{"question":"Quale candidata NFT?","action":"candidate"}
```

la risposta è stata corretta. Questo episodio è registrato come anomalia del comando/client usato nella singola prova, non come errore riprodotto nell'adapter.

## Test automatici

Il repository contiene `tests/test_comics_api.py`, ma nell'ambiente verificato `pytest` non era installato né sul Windows host né nell'immagine Docker API:

```text
pytest: comando non disponibile
python -m pytest: No module named pytest
```

Di conseguenza, in questa sessione non è stata dichiarata l'esecuzione dei test automatici. La validazione registrata qui è HTTP/manuale sul servizio Docker effettivamente avviato.

## Flusso locale verificato

1. Richiesta dei fumetti di Nicola (`gallery`) — **PASS**.
2. Apertura della scheda della tavola 01 (`detail`) — **PASS**.
3. Accesso al link pubblico dell'immagine restituito dalla scheda — link presente e versionato nel catalogo.
4. Richiesta della candidata NFT (`candidate`) — **PASS**.
5. Visualizzazione dello stato diritti e assenza di prova on-chain — **PASS**.
6. Richiesta dei prossimi passi (`next_steps`) — **PASS**.

## Stato del test

**Locale HTTP/manuale: PASS.** Il catalogo e l'adapter rispondono come previsto nell'ambiente locale verificato da Nicola.

**Test automatici pytest: NOT RUN in questa sessione.** Manca `pytest` nell'ambiente usato.

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
- `docs/nicola-comics/LOCAL-VALIDATION-NEXT.md` — piano di validazione locale.

## Prossima decisione richiesta

Individuare il responsabile del Zorgax pubblico e concordare hosting + autorizzazione dell'endpoint. Solo dopo questo passaggio il pilot può essere verificato end-to-end fuori dall'ambiente locale.
