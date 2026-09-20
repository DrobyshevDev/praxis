# «Скачал и запустил»: работает из коробки без токенов, ключей и GPU.
# Офлайн-режим (детерминированные компоненты) + полный корпус ГК. Для продового
# качества добавьте extra ml и GPU (см. docs/DEVELOPMENT.md).
FROM python:3.14-slim@sha256:caaf356f40667c496d405780745b9ac25771c189a51dfcc42430d531ea09f8a2
# Pinned by digest, not by tag. `python:3.14-slim` is republished whenever the
# base is rebuilt, so the image this Dockerfile produced last week and the one
# it produces today are not the same image and nothing records which was which.
# Dependabot raises the digest and the tag comment together.

WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
COPY corpus ./corpus

RUN pip install --no-cache-dir -e ".[api]"

ENV PRAXIS_CORPUS_DIR=/app/corpus \
    PRAXIS_OFFLINE=1

EXPOSE 8077
CMD ["uvicorn", "praxis.api.app:app", "--host", "0.0.0.0", "--port", "8077"]
