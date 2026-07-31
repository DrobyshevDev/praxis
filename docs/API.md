# Открытый API

Одно API-ядро обслуживает все клиенты: веб-UI, будущие desktop и mobile приложения и
сторонних ML-специалистов. API только на чтение, CORS открыт, схема машиночитаема.

## Запуск

```bash
pip install -e ".[api]"
uvicorn praxis.api.app:app --port 8077
# полный корпус:  PRAXIS_CORPUS_DIR=corpus uvicorn praxis.api.app:app --port 8077
```

- Интерактивная схема: `http://localhost:8077/docs`
- OpenAPI JSON: `http://localhost:8077/openapi.json`

## Эндпоинты

| Метод | Путь | Назначение |
|---|---|---|
| GET | `/health` | статус и версия |
| POST | `/v1/ask` | ответ на вопрос: нормы, span-подсветка, проверка цитат, трейс, практика |
| POST | `/v1/search` | сырой поиск норм по корпусу (гибрид + reranker), без генерации |
| GET | `/` | веб-UI |

## Примеры

```bash
curl -s http://localhost:8077/v1/ask \
  -H 'Content-Type: application/json' \
  -d '{"question":"можно ли расторгнуть договор через суд при нарушении"}'
```

```bash
curl -s http://localhost:8077/v1/search \
  -H 'Content-Type: application/json' \
  -d '{"query":"толкование договора","top_k":5}'
```

Python-клиент (только стандартная библиотека, [clients/python/praxis_client.py](../clients/python/praxis_client.py)):

```python
from praxis_client import PraxisClient

c = PraxisClient("http://localhost:8077")
ans = c.ask("что такое злоупотребление правом")
print(ans["confidence"], ans["text"])
for c_ in ans["citations"]:
    print(c_["citation"], c_["verdict"], c_["span"])

for hit in c.search("возмещение убытков", top_k=5):
    print(hit["citation"], hit["score"], hit["method"])
```

## Формат ответа `/v1/ask`

- `text` — ответ (экстрактивный по умолчанию, либо LLM-синтез с ключом).
- `confidence` — 0..1.
- `citations[]` — `citation`, `article_number`, `article_title`, `text`, `verdict`
  (`подтверждает` / `не относится` / `противоречит`), `span` (`[начало, конец)` в `text`).
- `unverified_claims[]` — тезисы без опоры на норму (не считать фактом).
- `steps[]` — трейс self-RAG.
- `related_cases[]` — судебная практика по процитированным нормам.

## Замечания по эксплуатации

- CORS открыт (`*`) — API на чтение, так удобно клиентам. Для продакшна с записью или
  приватным корпусом ограничьте источники и добавьте авторизацию.
- Пайплайн строится при первом запросе (ленивая инициализация моделей/корпуса).
- Резидентность данных: провайдер LLM выбирается конфигом (локальные модели, GigaChat,
  YandexGPT), корпус подключается локально через `PRAXIS_CORPUS_DIR`.
