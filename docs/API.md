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
| POST | `/v1/claim` | досудебная претензия по вопросу (обоснование из найденных норм) |
| POST | `/v1/lawsuit` | исковое заявление по вопросу |
| POST | `/v1/penalty` | калькулятор неустойки потребителю (ст. 23 / 28 ЗоЗПП) |
| POST | `/v1/fee` | калькулятор госпошлины в суд (ст. 333.19 / 333.36 НК) |
| POST | `/v1/interest` | калькулятор процентов (ст. 395 ГК) |
| POST | `/v1/contract` | чек-лист договора по нормам |
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

Python-клиент (только стандартная библиотека,
[clients/python/praxis_client.py](https://github.com/DrobyshevDev/praxis/blob/master/clients/python/praxis_client.py)):

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
- `citations[]` — `citation`, `code`, `article_number`, `article_title`, `text`, `verdict`
  (`подтверждает` / `не относится` / `противоречит`), `span` (`[начало, конец)` в `text`),
  `source_url` (ссылка «сверить с действующей редакцией»), `act_ref` (реквизиты акта,
  напр. `51-ФЗ от 30.11.1994`).
- `claim_applicable` — можно ли по этому вопросу собрать претензию/иск (`/v1/claim`, `/v1/lawsuit`).
- `unverified_claims[]` — тезисы без опоры на норму (не считать фактом).
- `steps[]` — трейс self-RAG.
- `related_cases[]` — судебная практика по процитированным нормам.

## Юридические задачи и калькуляторы

Поверх поиска — прикладные задачи. Претензия и иск строятся из **реально найденных норм**
(правовое обоснование цитирует их дословно), калькуляторы детерминированы и несут ссылку
на статью-основание. Всё это работает и на публичной демке в браузере:
[drobyshevdev.github.io/praxis/try](https://drobyshevdev.github.io/praxis/try/).

```bash
# Досудебная претензия (и аналогично /v1/lawsuit — исковое заявление)
curl -s http://localhost:8077/v1/claim \
  -H 'Content-Type: application/json' \
  -d '{"question":"можно ли вернуть телефон ненадлежащего качества"}'

# Неустойка потребителю: товар — 1%/день, услуга — 3%/день
curl -s http://localhost:8077/v1/penalty \
  -H 'Content-Type: application/json' \
  -d '{"price":50000,"days":10,"kind":"товар"}'

# Госпошлина в суд общей юрисдикции (для потребителя — с льготой ст. 333.36)
curl -s http://localhost:8077/v1/fee \
  -H 'Content-Type: application/json' \
  -d '{"amount":250000,"consumer":false}'

# Проценты по ст. 395 ГК (ставку ЦБ задаёт вызывающий)
curl -s http://localhost:8077/v1/interest \
  -H 'Content-Type: application/json' \
  -d '{"principal":200000,"rate_pct":16,"days":90}'

# Чек-лист договора
curl -s http://localhost:8077/v1/contract \
  -H 'Content-Type: application/json' \
  -d '{"text":"Договор... предмет... цена 40000 руб... возврату не подлежит"}'
```

- `/v1/claim` и `/v1/lawsuit` → `applicable`, `text`, `based_on[]` (нормы-основания),
  `note`, `disclaimer`.
- `/v1/penalty`, `/v1/fee`, `/v1/interest` → сумма, `breakdown` и `basis`
  (`citation`, `source_url`, `note`).
- `/v1/contract` → `checks[]` (`label`, `status` = `ok`/`missing`/`warning`, `citation`,
  `source_url`, `note`), `summary`, `disclaimer`.

## Замечания по эксплуатации

- CORS открыт (`*`) — API на чтение, так удобно клиентам. Для продакшна с записью или
  приватным корпусом ограничьте источники и добавьте авторизацию.
- Пайплайн строится при первом запросе (ленивая инициализация моделей/корпуса).
- Резидентность данных: провайдер LLM выбирается конфигом (локальные модели, GigaChat,
  YandexGPT), корпус подключается локально через `PRAXIS_CORPUS_DIR`.
