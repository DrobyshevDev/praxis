"""Полный пайплайн в CLI: вопрос → self-RAG → ответ с проверенными цитатами.

    python -m praxis.ask "можно ли расторгнуть договор через суд при нарушении"

Работает оффлайн на детерминированных fallback-компонентах. С ML-зависимостями и
ANTHROPIC_API_KEY те же вызовы используют BGE-M3, cross-encoder, NLI и Claude.
"""

from __future__ import annotations

import sys

from .core.models import Verdict
from .pipeline import build_pipeline

DEFAULT_QUESTION = "можно ли расторгнуть договор через суд при существенном нарушении"

_MARK = {Verdict.SUPPORTS: "✓", Verdict.CONTRADICTS: "✗", Verdict.UNRELATED: "?"}


def main() -> None:
    question = " ".join(sys.argv[1:]).strip() or DEFAULT_QUESTION
    pipeline = build_pipeline()
    answer = pipeline.answer(question)

    print(f"\n  ВОПРОС: {question}")
    print(f"  Уверенность: {answer.confidence:.0%}\n")
    print("  ОТВЕТ:")
    for line in answer.text.splitlines():
        print(f"  {line}")

    if answer.citations:
        print("\n  ИСТОЧНИКИ:")
        verdict_by_id = {vc.citation.provision.id: vc.verdict for vc in answer.verified}
        for c in answer.citations:
            mark = _MARK.get(verdict_by_id.get(c.provision.id), " ")
            print(f"   [{mark}] {c.provision.citation} — {c.provision.article_title}")

    if answer.unverified_claims:
        print("\n  ⚠ БЕЗ ОПОРЫ НА НОРМУ (не считать фактом):")
        for claim in answer.unverified_claims:
            print(f"   • {claim}")

    print("\n  ХОД РАССУЖДЕНИЯ:")
    for step in answer.steps:
        print(f"   → {step}")
    print()


if __name__ == "__main__":
    main()
