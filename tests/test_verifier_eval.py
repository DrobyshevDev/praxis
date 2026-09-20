"""Проверка того, что проверяет цитаты.

`NLIVerifier` — компонент, в честь которого назван продукт, — до появления этого
файла не встречался ни в одном тесте, и прогон golden set вызывал `verify()`
ноль раз за 18 вопросов. Здесь меряется он сам: тезис, норма, ожидаемый вердикт.

В CI гоняется офлайн-фолбэк: он без сети, без моделей и детерминирован. NLI
запускается руками (`python -m praxis.eval.verifier_runner --model ...`), потому
что тянуть с Hugging Face полгигабайта на каждый пуш — плохая сделка.
"""

from __future__ import annotations

from praxis.core.models import Verdict
from praxis.eval.verifier_runner import run_verifier_eval
from praxis.eval.verifier_set import VERIFIER_SET, counts_by_verdict
from praxis.ingest import load_sample_provisions
from praxis.verify.heuristic import HeuristicVerifier


def test_the_set_is_balanced() -> None:
    """Общая точность на перекошенном наборе прячет отказ, а не показывает его."""
    counts = counts_by_verdict()
    assert set(counts.values()) == {19}, counts


def test_every_labelled_pair_points_at_a_provision_that_exists() -> None:
    known = {p.id for p in load_sample_provisions()}
    unknown = sorted({c.provision_id for c in VERIFIER_SET} - known)
    assert not unknown, unknown


def test_every_provision_in_the_corpus_is_covered() -> None:
    """Норма без пары — норма, о которой верификатор ничего не обещает."""
    known = {p.id for p in load_sample_provisions()}
    uncovered = sorted(known - {c.provision_id for c in VERIFIER_SET})
    assert not uncovered, uncovered


def test_each_labelled_pair_says_why() -> None:
    """Эталон, разметку которого нельзя оспорить по существу, — не эталон."""
    silent = [c.claim[:60] for c in VERIFIER_SET if not c.why.strip()]
    assert not silent, silent


def test_the_offline_fallback_cannot_detect_a_contradiction() -> None:
    """Задокументированное ограничение, а не цель — и потому закреплено.

    `HeuristicVerifier` работает на лексическом пересечении, и отрицание в
    тезисе его не двигает: «должник обязан возместить убытки» и «должник не
    обязан возмещать убытки» для него одна и та же строка с точностью до слова.
    На наборе он берёт 0 из 19 противоречий, причём восемь из них называет
    подтверждением.

    Это имеет значение за пределами теста: офлайн-фолбэк — то, что работает в
    CI, в Docker-демо («docker compose up app, ключи не нужны») и везде, где нет
    torch. Утверждение README о том, что правдоподобная, но неверная ссылка
    будет поймана, к этому режиму не относится.

    Если фолбэк научится различать отрицание, тест упадёт — и вместе с ним
    надо будет поправить README и страницу проверок, а не только это число.
    """
    report = run_verifier_eval(HeuristicVerifier(), model="heuristic")
    contradictions = report.per_class[Verdict.CONTRADICTS.name]
    assert contradictions["correct"] == 0, (
        f"фолбэк распознал {contradictions['correct']} противоречий — "
        "ограничение изменилось, поправьте README и /checks/"
    )
    assert not report.always_same_answer


def test_the_offline_fallback_still_separates_support_from_irrelevance() -> None:
    """Что он всё-таки умеет — чтобы регрессия была видна.

    На классах SUPPORTS и UNRELATED фолбэк брал по 18 из 19. Пол в 0.8
    оставляет запас на одну ошибку сверх текущей и ловит обвал.
    """
    report = run_verifier_eval(HeuristicVerifier(), model="heuristic")
    for verdict in (Verdict.SUPPORTS, Verdict.UNRELATED):
        stats = report.per_class[verdict.name]
        assert stats["accuracy"] >= 0.8, (verdict.name, stats)


def test_the_report_names_a_verifier_that_answers_the_same_thing_every_time() -> None:
    """Худший отказ — один вердикт на всё: точность приличная, проверки нет."""

    class AlwaysSupports:
        def verify(self, claim, citation):
            from praxis.core.models import VerifiedClaim

            return VerifiedClaim(claim, citation, Verdict.SUPPORTS, 1.0)

    report = run_verifier_eval(AlwaysSupports(), model="always-supports")
    assert report.always_same_answer
    # Треть набора — SUPPORTS, так что общая точность выглядит неплохо для
    # компонента, который ничего не проверяет. Ради этого и макро-среднее.
    assert report.accuracy == round(19 / 57, 3)
    assert report.macro_accuracy < report.accuracy + 0.01
