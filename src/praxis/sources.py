"""Ссылки на действующую редакцию нормы во внешнем источнике.

Корпус — транскрипция (Викитека), редакция может отличаться от действующей. Чтобы
пользователь мог сверить одним кликом, для каждой нормы даём ссылку на текущий текст
статьи на zakonrf.info (per-article URL, актуальная редакция, все шесть кодексов).
"""

from __future__ import annotations

# act_id → slug на zakonrf.info (ЖК = jk, не zhk).
_SLUG = {
    "gk-rf": "gk",
    "uk-rf": "uk",
    "nk-rf": "nk",
    "tk-rf": "tk",
    "koap-rf": "koap",
    "zhk-rf": "jk",
}


def verify_url(act_id: str, article_number: str) -> str | None:
    """URL «сверить с действующей редакцией» для (акт, статья), или None."""
    slug = _SLUG.get(act_id)
    if slug is None and act_id:
        # sample-корпус нумерует акты (id вида "gk-rf-1") — отбрасываем числовой суффикс.
        head, _, tail = act_id.rpartition("-")
        if tail.isdigit():
            slug = _SLUG.get(head)
    if not slug or not article_number:
        return None
    return f"https://www.zakonrf.info/{slug}/{article_number}/"
