"""Eval-харнесс: golden set + метрики + HTML-дашборд качества.

RAGAS-faithfulness (требует LLM) подключается хуком; по умолчанию считаем
детерминированные метрики ретривера/цитат. Регрессии — на каждом релизе; трекаемые
прогоны (Run в метасторе, сравнение/drift) — через mlango в integrations/mlango_eval.
"""

from .golden import GOLDEN, GoldenCase
from .metrics import citation_precision, mrr, precision_at_k, recall_at_k
from .runner import EvalReport, run_eval

__all__ = [
    "GOLDEN",
    "EvalReport",
    "GoldenCase",
    "citation_precision",
    "mrr",
    "precision_at_k",
    "recall_at_k",
    "run_eval",
]
