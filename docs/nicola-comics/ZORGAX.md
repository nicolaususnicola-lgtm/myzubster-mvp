# Collegamento catalogo → assistente Zorgax

## Stato

Adapter in sola lettura implementato nel MVP locale. Legge il manifest versionato e restituisce le schede con link alle immagini pubblicate. Non richiede Ollama o Qdrant per consultare il catalogo.

Non è una distribuzione del Zorgax pubblico su myzubster.com: quel servizio deve essere configurato dal suo responsabile per chiamare questi endpoint in un ambiente raggiungibile. La prova con Nicola sul servizio pubblico resta aperta.

## Prova locale

Dopo aver aggiornato il repository, avviare `docker compose up --build -d`.

In PowerShell:

```powershell
$requestBody = @{ question = 'Mostrami i fumetti di Nicola'; action = 'gallery' } | ConvertTo-Json
$gallery = Invoke-RestMethod -Uri 'http://localhost:5000/api/zorgax/ask' -Method Post -ContentType 'application/json' -Body $requestBody
$gallery.answer
$gallery.sources | Select-Object comic_id,title,public_url
Invoke-RestMethod -Uri ('http://localhost:5000' + $gallery.sources[0].detail_url)
Start-Process $gallery.gallery_url
```

Le risposte devono contenere le tre nuove tavole; la prima è una candidata proposta, con diritti da verificare e campi on-chain vuoti.

## Contratto per il servizio Zorgax

- `GET /api/comics`: tre tavole create per Nicola.
- `GET /api/comics?include_references=true`: include anche i tre riferimenti precedenti.
- `GET /api/comics/{comic_id}`: scheda completa, o 404 per ID sconosciuto.
- `POST /api/zorgax/ask`: corpo JSON con `question` e `action`.
- `POST /api/ai/ask`: stesso corpo, con `topic: "nicola-comics"`, per usare l'API esistente.

Azioni: `gallery` (predefinita), `detail` (richiede `comic_id`), `candidate`, `next_steps`.

Il chiamante sceglie esplicitamente l'azione: questo adapter non interpreta liberamente il linguaggio naturale. `question` viene validata; la risposta viene costruita dai dati del catalogo, senza generazione AI. Il servizio Zorgax potrà mappare le intenzioni dell'utente alle azioni. Per richieste AI senza il topic esplicito rimane il flusso osservazioni/Ollama/Qdrant esistente.

Risposta: `answer`, `action`, `sources`, `gallery_url`, `mode: "catalog_adapter"`, `notice`. Ogni scheda include `detail_url` relativo all'host dell'API. Errori: 400 per richiesta non valida, 404 per scheda inesistente, 503 per catalogo non disponibile.

## Passaggio al servizio pubblico

1. Scegliere con il responsabile del Zorgax pubblico dove ospitare il MVP e come autorizzarne le chiamate.
2. Configurare il tool del servizio sulle azioni sopra indicate. Non esporre automaticamente tutto il MVP o il PC locale.
3. Provare: richiesta galleria → scheda → immagine → candidata e stato diritti.
4. Raccogliere il feedback di Nicola e registrare URL dell'ambiente e data della prova.

Nessuna azione di mint, wallet, pagamento o modifica del catalogo è esposta da questo adapter.
