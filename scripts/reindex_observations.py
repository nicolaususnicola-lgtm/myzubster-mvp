from src.api.server import _reindex_observations


def main():
    try:
        indexed = _reindex_observations()
    except Exception as error:
        print(f"Reindex fallito: {error}")
        return 1

    print(f"Reindex completato: {indexed} osservazioni indicizzate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
