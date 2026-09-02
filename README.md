# myzubster-mvp

Nicola IDEA MYZUBSTER

## Stato: MVP in sviluppo

> Questo progetto è in fase di sviluppo e validazione. Non è production-ready.

## Workflow

OBSERVE → DOCUMENT → CONNECT → COLLABORATE → VERIFY → PUBLISH → REWARD

## Avvio rapido con Docker

```bash
git clone https://github.com/nicolaususnicola-lgtm/myzubster-mvp.git
cd myzubster-mvp
docker compose up --build -d
docker compose ps
```

Quando il container è `healthy`, apri:

- `http://localhost:5000/api/observations`

In Docker l'API viene eseguita con Gunicorn. Docker invia `SIGTERM` e concede
15 secondi al processo per completare uno shutdown pulito.

Prova la creazione di un'osservazione:

```bash
curl -X POST http://localhost:5000/api/observation \
  -H "Content-Type: application/json" \
  -d '{"description":"Prova Docker","latitude":44.0678,"longitude":12.5695}'
```

Controlla i log:

```bash
docker compose logs -f api
```

I dati sono conservati nel volume Docker `observations-data` e rimangono
disponibili dopo il riavvio dei container.

```bash
# verifica il riavvio
docker compose restart api
docker compose ps

# arresta senza cancellare i dati
docker compose down

# verifica che non rimangano container attivi o terminati forzatamente
docker compose ps -a

# riavvia
docker compose up -d
```

Lo stop atteso è pulito. Se compare ancora `Exited (137)`, raccogli:

```bash
docker compose ps -a
docker compose logs --tail 100 api
docker inspect myzubster-mvp-api-1
```

> Non usare `docker compose down -v` se vuoi conservare le osservazioni:
> l'opzione `-v` elimina anche il volume dei dati.

## Avvio senza Docker

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python src/api/server.py
```

L'avvio diretto con `python src/api/server.py` usa il server Flask soltanto
per lo sviluppo locale. Il container usa Gunicorn.

## Test automatici

```bash
python -m pip install pytest
python -m pytest -v
```

## Contribuire

Vedi [CONTRIBUTING.md](CONTRIBUTING.md).

## Licenza

Vedi [LICENSE](LICENSE).

MYZ è un ledger interno di ricompensa e contabilità, non una valuta esterna.
