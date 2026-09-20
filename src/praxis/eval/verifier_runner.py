"""Прогон Citation Verifier по размеченному набору.

Меряет то, чего не меряет `runner.py`: не «нашлась ли норма», а «правильно ли
про неё сказано, подтверждает она тезис или нет».

Отчёт даёт точность по каждому классу отдельно и макро-среднее, а не одну общую
долю. Общая доля на несбалансированном ответе скрывает худший из возможных
отказов: верификатор, который на всё отвечает «подтверждает», получает
приличное число и не проверяет ничего. Матрица ошибок показывает это сразу.

    python -m praxis.eval.verifier_runner                    # текущая модель
    python -m praxis.eval.verifier_runner --heuristic        # офлайн-фолбэк
    python -m praxis.eval.verifier_runner --model <hf-id>    # любая NLI-модель
    python -m praxis.eval.verifier_runner --check 0.6        # упасть ниже порога
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import asdict, dataclass, field

from ..core.models import Citation, Verdict
from ..ingest import load_sample_provisions
from .verifier_set import VERIFIER_SET, VerifierCase

__all__ = ["VerifierReport", "run_verifier_eval"]


@dataclass
class CaseResult:
    provision: str
    claim: str
    expected: str
    actual: str
    score: float
    correct: bool
    why: str


@dataclass
class VerifierReport:
    model: str
    n: int
    seconds: float
    accuracy: float
    macro_accuracy: float
    per_class: dict = field(default_factory=dict)
    confusion: dict = field(default_factory=dict)
    cases: list = field(default_factory=list)

    @property
    def always_same_answer(self) -> bool:
        """True, когда верификатор выдал один и тот же вердикт на всё.

        Такой прогон может показать неплохую общую точность и при этом не
        проверять ничего, поэтому он называется отдельно.
        """
        answered = {row["actual"] for row in self.cases}
        return len(answered) == 1

    def summary(self) -> str:
        lines = [
            f"\n  Citation Verifier — {self.n} пар, {self.model}",
            f"    время                {self.seconds:.1f}s",
            f"    точность             {self.accuracy:.3f}",
            f"    макро-среднее        {self.macro_accuracy:.3f}",
            "",
            "    по классам:",
        ]
        for verdict, stats in self.per_class.items():
            lines.append(
                f"      {verdict:<14} {stats['correct']:>2}/{stats['total']:<2} = {stats['accuracy']:.3f}"
            )
        lines += ["", "    матрица (ожидалось → получено):"]
        for expected, row in self.confusion.items():
            got = ", ".join(f"{k} {v}" for k, v in row.items() if v)
            lines.append(f"      {expected:<14} {got}")
        if self.always_same_answer:
            lines += [
                "",
                "    ВНИМАНИЕ: один и тот же вердикт на все пары — такой",
                "    верификатор не проверяет ничего, какой бы ни была точность.",
            ]
        return "\n".join(lines)


def run_verifier_eval(verifier, cases: list[VerifierCase] | None = None, *, model: str = "?") -> VerifierReport:
    cases = cases or VERIFIER_SET
    by_id = {p.id: p for p in load_sample_provisions()}

    missing = sorted({c.provision_id for c in cases} - set(by_id))
    if missing:
        raise KeyError(f"нормы нет в корпусе-образце: {', '.join(missing)}")

    results: list[CaseResult] = []
    started = time.time()
    for case in cases:
        outcome = verifier.verify(case.claim, Citation(by_id[case.provision_id]))
        results.append(
            CaseResult(
                provision=by_id[case.provision_id].citation,
                claim=case.claim,
                expected=case.expected.name,
                actual=outcome.verdict.name,
                score=round(float(outcome.score), 4),
                correct=outcome.verdict is case.expected,
                why=case.why,
            )
        )
    elapsed = time.time() - started

    per_class: dict[str, dict] = {}
    confusion: dict[str, dict] = {}
    for verdict in Verdict:
        subset = [r for r in results if r.expected == verdict.name]
        correct = sum(1 for r in subset if r.correct)
        per_class[verdict.name] = {
            "total": len(subset),
            "correct": correct,
            "accuracy": round(correct / len(subset), 3) if subset else 0.0,
        }
        confusion[verdict.name] = {
            other.name: sum(1 for r in subset if r.actual == other.name) for other in Verdict
        }

    overall = sum(1 for r in results if r.correct) / len(results) if results else 0.0
    macro = (
        sum(stats["accuracy"] for stats in per_class.values() if stats["total"])
        / sum(1 for stats in per_class.values() if stats["total"])
        if per_class
        else 0.0
    )

    return VerifierReport(
        model=model,
        n=len(results),
        seconds=round(elapsed, 1),
        accuracy=round(overall, 3),
        macro_accuracy=round(macro, 3),
        per_class=per_class,
        confusion=confusion,
        cases=[asdict(r) for r in results],
    )


def _build(args) -> tuple[object, str]:
    if args.heuristic:
        from ..verify.heuristic import HeuristicVerifier

        return HeuristicVerifier(), "heuristic (офлайн-фолбэк)"
    from ..verify.nli import DEFAULT_MODEL, NLIVerifier

    name = args.model or DEFAULT_MODEL
    return NLIVerifier(model_name=name), name


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--heuristic", action="store_true", help="офлайн-фолбэк вместо NLI")
    parser.add_argument("--model", help="идентификатор модели на Hugging Face")
    parser.add_argument("--check", type=float, metavar="FLOOR",
                        help="выйти с ошибкой, если макро-среднее ниже порога")
    parser.add_argument("--json", action="store_true", help="выдать отчёт машинно")
    args = parser.parse_args()

    verifier, model = _build(args)
    report = run_verifier_eval(verifier, model=model)

    if args.json:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    else:
        print(report.summary())
        wrong = [r for r in report.cases if not r["correct"]]
        if wrong:
            print(f"\n    не сошлось ({len(wrong)}):")
            for row in wrong[:12]:
                print(f"      [{row['provision']}] ждали {row['expected']}, получили {row['actual']}")
                print(f"        «{row['claim'][:88]}»")
                print(f"        разметка: {row['why']}")

    if args.check is not None and report.macro_accuracy < args.check:
        print(f"\n  макро-среднее {report.macro_accuracy:.3f} ниже порога {args.check}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
