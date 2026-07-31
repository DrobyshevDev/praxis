"""Рендер HTML-дашборда качества из EvalReport (self-contained, theme-aware)."""

from __future__ import annotations

import html

_CSS = """
:root { color-scheme: light dark; --bg:#fff; --fg:#1a1a1a; --muted:#666;
  --card:#f6f7f9; --border:#e3e5e8; --good:#12855a; --bad:#c0392b; --accent:#2d6cdf; }
@media (prefers-color-scheme: dark) { :root { --bg:#15171a; --fg:#e8eaed;
  --muted:#9aa0a6; --card:#1e2126; --border:#2c3036; --good:#3fbe86; --bad:#e57373; } }
* { box-sizing:border-box; } body { margin:0; padding:32px; background:var(--bg);
  color:var(--fg); font:15px/1.5 -apple-system,Segoe UI,Roboto,sans-serif; }
h1 { font-size:22px; margin:0 0 4px; } .sub { color:var(--muted); margin-bottom:24px; }
.cards { display:flex; flex-wrap:wrap; gap:14px; margin-bottom:28px; }
.card { background:var(--card); border:1px solid var(--border); border-radius:12px;
  padding:16px 20px; min-width:150px; }
.card .val { font-size:28px; font-weight:700; } .card .lbl { color:var(--muted); font-size:13px; }
table { width:100%; border-collapse:collapse; font-size:14px; }
th,td { text-align:left; padding:9px 10px; border-bottom:1px solid var(--border);
  vertical-align:top; } th { color:var(--muted); font-weight:600; }
.q { max-width:340px; } code { background:var(--card); padding:1px 5px; border-radius:5px; }
.hit { color:var(--good); font-weight:700; } .miss { color:var(--bad); font-weight:700; }
.bar { height:6px; border-radius:4px; background:var(--border); overflow:hidden; margin-top:3px; }
.bar > i { display:block; height:100%; background:var(--accent); }
"""


def _card(value: float, label: str) -> str:
    return f'<div class="card"><div class="val">{value:.2f}</div><div class="lbl">{html.escape(label)}</div></div>'


def _row(case: dict, k: int) -> str:
    q = html.escape(case["question"])
    relevant = ", ".join(case["relevant"])
    cited = ", ".join(case["cited"]) or "—"
    hit = '<span class="hit">✓</span>' if case["hit"] else '<span class="miss">✗</span>'
    conf = case["confidence"]
    conf_pct = int(round(conf * 100))
    return (
        f"<tr><td class='q'>{q}</td>"
        f"<td><code>{relevant}</code></td>"
        f"<td><code>{html.escape(cited)}</code></td>"
        f"<td>{case[f'recall_at_k']:.2f}</td>"
        f"<td>{case['mrr']:.2f}</td>"
        f"<td>{case['citation_precision']:.2f}</td>"
        f"<td>{hit}</td>"
        f"<td>{conf:.2f}<div class='bar'><i style='width:{conf_pct}%'></i></div></td></tr>"
    )


def render_html(report) -> str:
    agg = report.aggregate
    cards = "".join(_card(v, name) for name, v in agg.items())
    rows = "".join(_row(c, report.k) for c in report.cases)
    return (
        "<!doctype html><html lang='ru'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width, initial-scale=1'>"
        f"<title>Praxis — качество ретривера</title><style>{_CSS}</style></head><body>"
        "<h1>Praxis — дашборд качества</h1>"
        f"<div class='sub'>Golden set: {report.n} кейсов · k={report.k} · "
        "детерминированный офлайн-прогон (BM25+hybrid+lexical rerank+эвристический verifier)</div>"
        f"<div class='cards'>{cards}</div>"
        "<table><thead><tr><th>Вопрос</th><th>Ожид. статьи</th><th>Процитированы</th>"
        f"<th>recall@{report.k}</th><th>MRR</th><th>cite-prec</th><th>hit</th>"
        "<th>уверенность</th></tr></thead>"
        f"<tbody>{rows}</tbody></table></body></html>"
    )
