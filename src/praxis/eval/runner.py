"""Прогон пайплайна по golden set → агрегированные метрики + отчёт (JSON/HTML)."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field

from ..pipeline import build_pipeline
from .golden import GOLDEN, GoldenCase
from .metrics import citation_precision, dedupe, mrr, recall_at_k
from .report import render_html


@dataclass
class CaseResult:
    question: str
    relevant: list[str]
    retrieved: list[str]
    cited: list[str]
    recall_at_k: float
    mrr: float
    citation_precision: float
    hit: bool
    confidence: float


@dataclass
class EvalReport:
    k: int
    n: int
    aggregate: dict = field(default_factory=dict)
    cases: list[dict] = field(default_factory=list)


def _mean(values: list[float]) -> float:
    return round(sum(values) / len(values), 3) if values else 0.0


def run_eval(pipeline=None, cases: list[GoldenCase] | None = None, k: int = 5) -> EvalReport:
    pipeline = pipeline or build_pipeline()
    cases = cases or GOLDEN
    results: list[CaseResult] = []

    for case in cases:
        candidates = pipeline.retriever.search(case.question, top_k=10)
        if pipeline.reranker is not None:
            candidates = pipeline.reranker.rerank(case.question, candidates, top_k=10)
        retrieved = dedupe(c.provision.article_number for c in candidates)

        answer = pipeline.answer(case.question)
        cited = dedupe(c.provision.article_number for c in answer.citations)

        results.append(
            CaseResult(
                question=case.question,
                relevant=sorted(case.relevant),
                retrieved=retrieved,
                cited=cited,
                recall_at_k=round(recall_at_k(retrieved, case.relevant, k), 3),
                mrr=round(mrr(retrieved, case.relevant), 3),
                citation_precision=round(citation_precision(cited, case.relevant), 3),
                hit=bool(set(cited) & case.relevant),
                confidence=answer.confidence,
            )
        )

    aggregate = {
        f"recall@{k}": _mean([r.recall_at_k for r in results]),
        "mrr": _mean([r.mrr for r in results]),
        "citation_precision": _mean([r.citation_precision for r in results]),
        "hit_rate": _mean([1.0 if r.hit else 0.0 for r in results]),
        "mean_confidence": _mean([r.confidence for r in results]),
    }
    return EvalReport(
        k=k, n=len(results), aggregate=aggregate, cases=[asdict(r) for r in results]
    )


def main() -> None:
    report = run_eval()
    os.makedirs("reports", exist_ok=True)
    with open("reports/eval.json", "w", encoding="utf-8") as f:
        json.dump(asdict(report), f, ensure_ascii=False, indent=2)
    with open("reports/eval.html", "w", encoding="utf-8") as f:
        f.write(render_html(report))

    print(f"\n  Praxis eval — {report.n} кейсов, k={report.k}\n")
    for name, value in report.aggregate.items():
        print(f"    {name:>20}: {value:.3f}")
    print("\n  Отчёт: reports/eval.html, reports/eval.json\n")


if __name__ == "__main__":
    main()
