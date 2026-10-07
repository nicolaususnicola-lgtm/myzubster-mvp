FROM python:3.12-alpine

WORKDIR /app

COPY agent.py /app/agent.py

RUN addgroup -S n4k48 && adduser -S -G n4k48 n4k48
USER n4k48

CMD ["python", "/app/agent.py"]
