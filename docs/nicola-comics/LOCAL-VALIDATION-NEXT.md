# Nicola Comics × MyZubster — prossima validazione locale

Data: 15 settembre 2026

## Obiettivo

Validare sul PC il percorso completo del catalog adapter prima del collegamento al Zorgax pubblico, mantenendo una separazione esplicita tra funzionalità già verificabili localmente e integrazioni ancora da configurare.

## Problemi incontrati finora

Nel test locale già documentato non sono emersi errori bloccanti nel catalogo o nell'adapter. Il principale limite operativo è esterno al test locale: il servizio non è ancora collegato al Zorgax pubblico e restano da definire hosting, autorizzazione e configurazione dell'endpoint pubblico.

Il primo report non documentava inoltre in modo esplicito, uno per uno, tutti i percorsi `gallery`, `detail`, `candidate`, `next_steps` e i principali casi di errore. Questa è quindi la prossima area da validare in modo riproducibile.

## Test proposto sul PC

Avviare/ricostruire il servizio:

```text
docker compose up --build -d
```

Quindi verificare il flusso:

1. **Gallery** — `POST /api/zorgax/ask` con `action: gallery` deve restituire le tre tavole create per il pilot.
2. **Detail** — richiedere `n4k48-comic-001` e verificare che scheda, immagine/link e metadati corrispondano al catalogo.
3. **Candidate** — `action: candidate` deve restituire soltanto `n4k48-comic-001`, con `NFT_CANDIDATE` e `PROPOSED_FOR_REVIEW`.
4. **Rights / on-chain boundary** — verificare che la candidata mantenga `rights_status: TO_VERIFY` e che non venga presentata alcuna transazione/mint come esistente.
5. **Next steps** — `action: next_steps` deve indicare esplicitamente la verifica di provenienza/autorizzazioni e il futuro collegamento al Zorgax pubblico, senza eseguire mint.
6. **Error handling** — verificare almeno: JSON mancante/non valido → 400; `detail` senza `comic_id` → 400; fumetto inesistente → 404; azione non consentita (es. `mint`) → 400.

## Test automatici già presenti

`tests/test_comics_api.py` copre già:

- percorso completo catalogo → dettaglio e verifica degli asset;
- esclusione predefinita dei riferimenti esterni;
- candidata proposta e non mintata;
- routing esplicito del topic Nicola Comics;
- richieste non valide e 404;
- errore controllato del catalogo;
- confine tra adapter locale e integrazione Zorgax pubblica.

Eseguire:

```text
pytest -q tests/test_comics_api.py
```

## Criterio PASS

La validazione è **PASS** se tutti i test automatici passano e le risposte manuali mantengono coerentemente:

- 3 tavole del pilot nella gallery;
- tavola 01 come unica candidata proposta;
- diritti `TO_VERIFY`;
- nessuna prova o dichiarazione di mint;
- errori HTTP controllati;
- Zorgax pubblico indicato come integrazione ancora da verificare.

## Dopo il PASS

Registrare data, ambiente, risultato di `pytest`, eventuali anomalie e output essenziali in un nuovo test report. A quel punto il prossimo blocco da risolvere con MyZubster è la configurazione dell'endpoint raggiungibile dal Zorgax pubblico.
