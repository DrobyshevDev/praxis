# Разработка

## Скачал и запустил (Docker, без токенов)

Полный функционал без ключей, платных сервисов и GPU — офлайн-режим на полном корпусе ГК:

```bash
git clone https://github.com/DrobyshevDev/praxis && cd praxis
docker compose up app
# http://localhost:8077
```

Продовое качество (реальные модели BGE-M3 / reranker / NLI) включается extra `ml` и GPU —
см. ниже. Claude для синтеза — по желанию, через `ANTHROPIC_API_KEY`, но не обязателен.

## Быстрый старт (без зависимостей)

Весь пайплайн работает **офлайн, на чистой стандартной библиотеке** — детерминированные
fallback-компоненты. Python 3.11+.

```bash
# из корня репозитория
python -m pytest -q                                  # тесты (pip install pytest)
PYTHONPATH=src python -m praxis.ask "можно ли расторгнуть договор через суд"
PYTHONPATH=src python -m praxis.demo "толкование договора"   # только BM25-срез
PYTHONPATH=src python -m praxis.eval                 # прогон метрик → reports/
```

Windows PowerShell:

```powershell
$env:PYTHONPATH="src"; python -m praxis.ask "можно ли расторгнуть договор через суд"
```

Или editable-установка с консольными командами:

```bash
pip install -e ".[dev]"
praxis-ask "как суд толкует неясное условие договора"
praxis-eval
pytest -q
```

## Веб-API и UI

```bash
pip install -e ".[api]"
uvicorn praxis.api.app:app --port 8077
# открыть http://127.0.0.1:8077  — простой UI
# POST /ask {"question": "..."}  ·  POST /search {"query":"...","top_k":5}  ·  GET /health
```

## Реальные модели и LLM (продакшн-путь)

Один и тот же код: `default_*()` сами включают реальные реализации при наличии
зависимостей/ключей — менять ничего не надо.

```bash
pip install -e ".[ml]"     # BGE-M3, cross-encoder reranker, NLI-верификатор (GPU)
pip install -e ".[llm]"    # Claude
export ANTHROPIC_API_KEY=...   # включает LLM-синтез вместо экстрактивного ответа
docker compose up -d           # Postgres + pgvector (реальный индекс), порт 5434
```

## Что где

| Пакет | Назначение | Статус |
|-------|-----------|--------|
| `core` | доменные модели (Акт→Статья→Норма→Цитата) | ✅ |
| `ingest` | источники, нормализация, легал-aware чанкинг | ✅ (образец) |
| `embed` | BGE-M3 (реальный) + hashing fallback | ✅ |
| `retrieve` | BM25 + dense + hybrid RRF | ✅ |
| `rerank` | cross-encoder BGE + лексический fallback | ✅ |
| `verify` | Citation Verifier: NLI + эвристика | ✅ |
| `llm` / `generate` | Claude/Mock + экстрактивный/LLM генератор | ✅ |
| `agent` | self-RAG луп с трейсом | ✅ |
| `eval` | golden set, метрики, HTML-дашборд | ✅ |
| `api` | FastAPI + веб-UI | ✅ |
| `index` | схема Postgres + pgvector | ✅ (SQL) |

## Договорённости

- Ветка по умолчанию — `master`.
- Тексты норм в `ingest/sources` — **образец, не сверенная редакция**. Реальный корпус
  (официальный текст с pravo.gov.ru + реквизиты редакции) подключается тем же контрактом.
- Каждый ML-компонент pluggable: реальная реализация на GPU/API + детерминированный
  офлайн-fallback. Поэтому тесты и демо не требуют скачивания моделей.
