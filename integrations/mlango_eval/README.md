# mlango_eval — трекаемый eval Praxis

Опциональный [mlango](https://github.com/DrobyshevDev/mlango)-проект: гоняет golden-set
eval Praxis через подсистему evals mlango. Каждый прогон становится Run в метасторе с
метриками (recall/hit/confidence) и результатами по кейсам, так что регрессия видна как
diff между прогонами (`runs compare`), а не как забытое число.

Это отдельная интеграция — ядро Praxis (пакет `praxis`) от mlango не зависит.

## Запуск

```bash
pip install mlango                 # praxis подхватывается из ../../src (см. settings.py)
python manage.py migrate
python manage.py evaluate demo.PraxisRetrieval
python manage.py runs list         # прогон записан в метасторе
python manage.py runs compare <id1> <id2>   # что изменилось между прогонами
python manage.py runserver         # admin с golden set и прогонами на :8000/admin/
```

## Что где

| Путь | Что |
|---|---|
| `demo/datasets.py` | `Dataset` над `praxis.eval.golden.GOLDEN` |
| `demo/evals.py` | `Eval`: `predict()` гоняет пайплайн Praxis, `score()` — recall/hit по цитатам |
| `mlango_eval/settings.py` | добавляет `../../src` в path, форсит PRAXIS_OFFLINE |

По умолчанию eval идёт офлайн-детерминированно (без GPU/сети). Для прогона на реальном
корпусе задайте `PRAXIS_CORPUS_DIR`.
