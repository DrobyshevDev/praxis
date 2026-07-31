# Разработка

## Быстрый старт (v0)

v0-срез (ingest + BM25) работает **без зависимостей и без БД** — только стандартная
библиотека Python 3.11+.

```bash
# из корня репозитория
python -m pytest -q                       # тесты (нужен pytest: pip install pytest)
PYTHONPATH=src python -m praxis.demo "толкование неясного условия договора"
```

Windows PowerShell:

```powershell
$env:PYTHONPATH="src"; python -m praxis.demo "толкование неясного условия договора"
```

Или установить пакет в editable-режиме и пользоваться консольной командой:

```bash
pip install -e ".[dev]"
praxis-demo "как расторгнуть договор через суд"
pytest -q
```

## Инфраструктура (нужна с v1)

Реальный индекс (dense/hybrid) живёт в Postgres + pgvector:

```bash
docker compose up -d          # поднимет БД на порту 5434 и применит schema.sql
```

ML-модели (эмбеддинги BGE-M3, reranker, NLI-верификатор) — тяжёлые, ставятся
отдельным extra и гоняются на GPU:

```bash
pip install -e ".[ml]"
```

## Что где

| Пакет | Назначение | Статус |
|-------|-----------|--------|
| `core` | доменные модели (Акт→Статья→Норма→Цитата) | ✅ v0 |
| `ingest` | источники, нормализация, легал-aware чанкинг | ✅ v0 (образец) |
| `retrieve` | BM25 baseline; hybrid + rerank | ✅ BM25 / 🔜 v1 |
| `index` | схема Postgres + pgvector | 🔜 v1 |
| `verify` | Citation Verifier (NLI) | 🔜 v1 (контракт готов) |
| `agent` | self-RAG на glia | 🔜 v1 |
| `generate` | сборка ответа со span-цитатами | 🔜 v1 |
| `eval` | RAGAS + legal-метрики, дашборд | 🔜 v1 |
| `api` | FastAPI | 🔜 v1 |

## Договорённости

- Ветка по умолчанию — `master`.
- Тексты норм в `ingest/sources` на v0 — **образец, не сверенная редакция**. На v1
  заменяются официальным машиночитаемым текстом с pravo.gov.ru (с реквизитами).
