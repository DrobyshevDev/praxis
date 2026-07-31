"""Eval Praxis в mlango — трекаемый прогон ретривера по golden set.

Реальное использование mlango: `python manage.py evaluate demo.PraxisRetrieval` заводит
Run в метасторе, пишет метрики (recall/hit) и результаты по кейсам. Два прогона можно
сравнить (`manage.py runs compare`) — регрессия видна как diff, а не как забытое число.
predict() гоняет пайплайн Praxis, score() считает recall/hit по процитированным статьям.
"""

from mlango.evals import Eval

from demo.datasets import GoldenCases
from praxis.pipeline import build_pipeline


def _cited_articles(answer) -> set[str]:
    return {c.provision.article_number for c in answer.citations}


class PraxisRetrieval(Eval):
    """Находит ли Praxis эталонные статьи для юридических вопросов."""

    _pipeline = None

    class Meta:
        dataset = GoldenCases
        target = build_pipeline  # прогон делаем в predict()
        input_field = "question"
        expected_field = "expected"
        case_id_field = "id"
        threshold = 0.5

    def predict(self, case):
        if PraxisRetrieval._pipeline is None:
            PraxisRetrieval._pipeline = build_pipeline()
        return PraxisRetrieval._pipeline.answer(case.get("question"))

    def score(self, case, output):
        expected = set(str(case.get("expected") or "").split())
        cited = _cited_articles(output)
        recall = len(cited & expected) / len(expected) if expected else 0.0
        return {
            "recall": round(recall, 3),
            "hit": 1.0 if (cited & expected) else 0.0,
            "confidence": round(getattr(output, "confidence", 0.0), 3),
        }
