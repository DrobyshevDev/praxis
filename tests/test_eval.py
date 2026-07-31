from praxis.eval import run_eval
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
    assert report.n == 12
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
