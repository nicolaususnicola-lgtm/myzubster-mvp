# Collegamento catalogo → assistente Zorgax

## Stato

Adapter in sola lettura implementato e verificato nel MVP locale. Legge il manifest versionato e restituisce le schede con link alle immagini pubblicate. Non richiede Ollama o Qdrant per consultare il catalogo.

Il passaggio successivo è il test con il Zorgax pubblico. L'endpoint del pilot deve essere ospitato in un ambiente raggiungibile e separato dal PC locale di Nicola. Il coordinamento tecnico avviene nella issue MyZubster #1176.

## Configurazione

L'adapter non contiene un URL locale hardcoded per l'integrazione pubblica. La base URL pubblica può essere fornita dall'ambiente di hosting:

```text
NICOLA_COMICS_BASE_URL=https://pilot.example.org
```

La variabile è opzionale in locale. Se non è impostata, `detail_url` resta relativo, per esempio `/api/comics/n4k48-comic-001`. Se è impostata, `detail_url` viene restituito come URL assoluto basato su `NICOLA_COMICS_BASE_URL`.

Non inserire token, password, chiavi o altri segreti nel repository. L'autenticazione definitiva deve essere configurata nell'ambiente di hosting/pubblico.

## Prova locale

Dopo aver aggiornato il repository, avviare:

```text
docker compose up --build -d
```

In PowerShell:

```powershell
$requestBody = @{ question = 'Mostrami i fumetti di Nicola'; action = 'gallery' } | ConvertTo-Json
$gallery = Invoke-RestMethod -Uri 'http://localhost:5000/api/zorgax/ask' -Method Post -ContentType 'application/json' -Body $requestBody
$gallery.answer
$gallery.sources | Select-Object comic_id,title,public_url,detail_url
```

La risposta deve contenere le tre tavole del pilot. La prima resta una candidata proposta, con diritti da verificare e campi on-chain vuoti.

## Endpoint pubblici richiesti

### `GET /api/comics`

Restituisce le tre tavole create per Nicola. Parametro opzionale `include_references=true` per includere anche i riferimenti precedenti.

### `GET /api/comics/{comic_id}`

Restituisce una singola scheda completa. Un ID sconosciuto produce HTTP 404.

### `POST /api/zorgax/ask`

Corpo JSON:

```json
{
  "question": "Mostrami i fumetti di Nicola",
  "action": "gallery"
}
```

Azioni supportate:

- `gallery` — predefinita; restituisce le tre tavole del pilot;
- `detail` — richiede `comic_id`;
- `candidate` — restituisce la candidata NFT proposta;
- `next_steps` — restituisce i passaggi ancora da verificare.

Esempio detail:

```json
{
  "question": "Mostrami la scheda della tavola 01",
  "action": "detail",
  "comic_id": "n4k48-comic-001"
}
```

Esempio candidate:

```json
{
  "question": "Quale candidata NFT?",
  "action": "candidate"
}
```

### `POST /api/ai/ask`

Compatibilità con l'API esistente usando lo stesso payload più `topic: "nicola-comics"`.

## Risposta

Le risposte dell'adapter includono:

- `answer`;
- `action`;
- `sources`;
- `gallery_url`;
- `api_base_url` (`null` se la base pubblica non è configurata);
- `mode: "catalog_adapter"`;
- `notice`.

Ogni scheda include `detail_url`, relativo oppure assoluto in base a `NICOLA_COMICS_BASE_URL`.

Errori previsti: HTTP 400 per richiesta non valida, 404 per scheda inesistente, 503 per catalogo non disponibile.

## Vincoli del pilot

Il chiamante sceglie esplicitamente l'azione: l'adapter non interpreta liberamente il linguaggio naturale. Il servizio Zorgax pubblico potrà mappare le intenzioni dell'utente alle quattro azioni supportate.

Il pilot resta in sola lettura. Nessuna azione di mint, wallet, pagamento o modifica del catalogo è esposta. `n4k48-comic-001` resta `NFT_CANDIDATE / PROPOSED_FOR_REVIEW`; i diritti restano `TO_VERIFY` e i campi on-chain devono rimanere vuoti finché non esiste una prova verificata.

## Test end-to-end pubblico da preparare

Percorso concordato:

1. richiesta dei fumetti;
2. `gallery`;
3. `detail` / card;
4. apertura dell'immagine pubblicata;
5. `candidate`;
6. visualizzazione di `rights_status` e stato/prova on-chain.

Per completare la prova servono lato MyZubster/hosting:

- URL HTTPS pubblico del pilot;
- configurazione di `NICOLA_COMICS_BASE_URL`;
- eventuale autenticazione/autorizzazione gestita come segreto dell'ambiente;
- configurazione del Zorgax pubblico per mappare le intenzioni alle azioni;
- data e ambiente della prova end-to-end.

Non esporre il PC locale di Nicola e non committare segreti.