import pathlib
import re

from praxis.eval import run_eval
from praxis.eval.golden import GOLDEN
from praxis.eval.metrics import citation_precision, mrr, recall_at_k
from praxis.eval.report import render_html


def test_metric_functions():
    ranked = ["450", "431", "10"]
    assert recall_at_k(ranked, {"431"}, k=5) == 1.0
    assert recall_at_k(ranked, {"999"}, k=5) == 0.0
    assert mrr(ranked, {"431"}) == 0.5
    assert citation_precision(["450", "10"], {"450"}) == 0.5
    assert citation_precision([], {"450"}) == 0.0


def test_run_eval_produces_report():
    report = run_eval()
    assert report.n == len(GOLDEN)
    assert set(report.aggregate) >= {"recall@5", "mrr", "citation_precision", "hit_rate"}
    # На образце корпуса ретривер должен находить релевантную статью в большинстве кейсов.
    assert report.aggregate["recall@5"] >= 0.7
    assert 0.0 <= report.aggregate["mean_confidence"] <= 1.0


def test_render_html_is_selfcontained():
    report = run_eval()
    out = render_html(report)
    assert out.startswith("<!doctype html>")
    assert "Praxis" in out and "recall@5" in out
    assert "http://" not in out and "https://" not in out  # без внешних ресурсов


def test_readmes_quote_the_real_golden_set_size():
    """Оба README называют размер набора, и оба называли его неверно.

    В наборе 18 вопросов; README говорили про 12 — столько было, когда абзац
    писали. Цифру в прозе никто не пересчитывал, а читатель по ней судит,
    насколько всерьёз измерена заявленная в той же таблице метрика.
    """
    root = pathlib.Path(__file__).resolve().parents[1]
    for name in ("README.md", "README.en.md"):
        text = (root / name).read_text(encoding="utf-8")
        match = re.search(r"golden set \((\d+) (?:questions|вопросов)", text)
        assert match, f"{name}: размер golden set больше не указан в ожидаемой форме"
        assert int(match.group(1)) == len(GOLDEN), name


# Названия строк таблицы качества в README -> ключи в aggregate.
_TABLE_ROWS = {
    "recall@5": "recall@5",
    "MRR": "mrr",
    "hit-rate": "hit_rate",
    "mean confidence": "mean_confidence",
    "citation precision": "citation_precision",
}


def _offline_column(text: str) -> dict[str, float]:
    """Правая колонка таблицы качества: офлайн-fallback."""
    found: dict[str, float] = {}
    for label in _TABLE_ROWS:
        match = re.search(rf"^\| *{re.escape(label)} *\| *[\d.]+ *\| *([\d.]+) *\|", text, re.MULTILINE)
        if match:
            found[label] = float(match.group(1))
    return found


def test_readme_offline_column_matches_a_fresh_run(monkeypatch):
    """Офлайн-колонка таблицы качества — это то, что печатает прогон.

    Колонку замеряли на наборе из двенадцати вопросов, набор вырос до
    восемнадцати, и три числа из пяти перестали быть верными: recall@5 стоял
    1.00 при 0.972, MRR 0.90 при 0.935, confidence 0.63 при 0.59. Замер никто
    не повторял, потому что повторять его было нечему.

    Офлайн-путь детерминирован — ни моделей, ни сети, ни случайности, — поэтому
    его, в отличие от колонки с реальными моделями, можно держать тестом.
    Колонка с GPU остаётся непроверенной честно: её держит железо, которого в CI
    нет.
    """
    monkeypatch.setenv("PRAXIS_OFFLINE", "1")
    measured = run_eval().aggregate

    root = pathlib.Path(__file__).resolve().parents[1]
    for name in ("README.md", "README.en.md"):
        stated = _offline_column((root / name).read_text(encoding="utf-8"))
        assert set(stated) == set(_TABLE_ROWS), f"{name}: таблица качества изменила форму"
        for label, key in _TABLE_ROWS.items():
            # Допуск — половина последнего разряда: заявленное должно быть
            # правильным округлением измеренного до двух знаков.
            assert abs(stated[label] - measured[key]) <= 0.005 + 1e-9, (
                f"{name}: {label} заявлен как {stated[label]}, прогон даёт {measured[key]:.3f}"
            )
