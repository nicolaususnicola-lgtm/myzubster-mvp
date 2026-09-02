FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MYZUBSTER_HOST=0.0.0.0 \
    MYZUBSTER_PORT=5000 \
    MYZUBSTER_OBSERVATIONS_FILE=/data/observations.json

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --requirement requirements.txt \
    && useradd --create-home --uid 10001 myzubster \
    && mkdir -p /data \
    && chown myzubster:myzubster /data

COPY --chown=myzubster:myzubster . .

USER myzubster

EXPOSE 5000

HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=5 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/api/observations', timeout=2)" || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "4", "--timeout", "30", "--graceful-timeout", "10", "--access-logfile", "-", "--error-logfile", "-", "src.api.server:app"]
