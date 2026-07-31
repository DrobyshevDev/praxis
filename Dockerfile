# «Скачал и запустил»: работает из коробки без токенов, ключей и GPU.
# Офлайн-режим (детерминированные компоненты) + полный корпус ГК. Для продового
# качества добавьте extra ml и GPU (см. docs/DEVELOPMENT.md).
FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
COPY corpus ./corpus

RUN pip install --no-cache-dir -e ".[api]"

ENV PRAXIS_CORPUS_DIR=/app/corpus \
    PRAXIS_OFFLINE=1

EXPOSE 8077
CMD ["uvicorn", "praxis.api.app:app", "--host", "0.0.0.0", "--port", "8077"]
