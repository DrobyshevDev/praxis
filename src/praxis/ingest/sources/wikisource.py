"""Выгрузка текста кодексов с Викитеки (ru.wikisource.org) через MediaWiki API.

Викитека — свободный контент (официальные правовые тексты — общественное достояние,
ст. 1259 ГК РФ), API предназначен для переиспользования. Оговорка: это транскрипция;
актуальность редакции нужно сверять с pravo.gov.ru перед юридическим использованием.

Пайплайн: список глав → wikitext каждой → очистка разметки → parse_statute_text.
"""

from __future__ import annotations

import json
import re
import time
import urllib.parse
import urllib.request

from ...core.models import ActKind
from ..schema import RawAct
from ..statute_parser import parse_statute_text

_API = "https://ru.wikisource.org/w/api.php"
_UA = "praxis-ingest/0.1 (+https://github.com/DrobyshevDev/praxis)"


def _api(params: dict) -> dict:
    query = urllib.parse.urlencode(dict(params, format="json", redirects="1"))
    req = urllib.request.Request(f"{_API}?{query}", headers={"User-Agent": _UA})
    with urllib.request.urlopen(req, timeout=30) as r:  # noqa: S310
        return json.load(r)


def list_chapter_titles(prefix: str, limit: int = 500) -> list[str]:
    """Страницы глав вида '<prefix> <N>' (без под-подстраниц), по возрастанию N."""
    titles: list[str] = []
    cont: str | None = None
    while True:
        params = {"action": "query", "list": "allpages", "apprefix": prefix, "aplimit": "200"}
        if cont:
            params["apcontinue"] = cont
        data = _api(params)
        titles += [p["title"] for p in data["query"]["allpages"]]
        cont = data.get("continue", {}).get("apcontinue")
        if not cont or len(titles) >= limit:
            break
    pat = re.compile(re.escape(prefix) + r" (\d+)$")
    chapters = [(int(m.group(1)), t) for t in titles if (m := pat.fullmatch(t))]
    return [t for _, t in sorted(chapters)]


def fetch_wikitext(title: str) -> str:
    return _api({"action": "parse", "page": title, "prop": "wikitext"})["parse"]["wikitext"]["*"]


def clean_wikitext(wt: str) -> str:
    """Вики-разметку → плоский текст в формате parse_statute_text (Статья N. / пункты)."""
    wt = re.sub(r"<ref[^>]*>.*?</ref>", "", wt, flags=re.S)
    wt = re.sub(r"<ref[^>]*/>", "", wt)
    prev = None
    while prev != wt:  # шаблоны {{...}}, возможно вложенные
        prev = wt
        wt = re.sub(r"\{\{[^{}]*\}\}", "", wt)
    wt = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]+)\]\]", r"\1", wt)  # [[t|text]] -> text
    wt = re.sub(r"\[https?://\S+\s+([^\]]+)\]", r"\1", wt)
    wt = re.sub(r"\[https?://\S+\]", "", wt)
    wt = re.sub(r"^=+\s*(.*?)\s*=+\s*$", r"\1", wt, flags=re.M)  # ===== Статья ===== -> Статья
    wt = wt.replace("'''", "").replace("''", "")
    wt = re.sub(r"<[^>]+>", "", wt)
    wt = re.sub(r"\((?:в ред\.|введена|введён|в редакции)[^)]*\)", "", wt)
    lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in wt.splitlines()]
    lines = [
        ln for ln in lines
        if ln and not re.match(r"^(Глава|Раздел|Подраздел|Параграф|§)\b", ln)
    ]
    return "\n".join(lines)


def fetch_page_act(
    page_title: str,
    *,
    id: str,
    title: str,
    short_title: str,
    kind: ActKind = ActKind.FEDERAL_LAW,
    number: str | None = None,
    date: str | None = None,
    edition: str | None = None,
) -> RawAct:
    """Акт, размещённый одной страницей (ФЗ без глав-подстраниц, напр. ЗоЗПП)."""
    text = clean_wikitext(fetch_wikitext(page_title))
    return parse_statute_text(
        text,
        id=id,
        title=title,
        short_title=short_title,
        kind=kind,
        number=number,
        date=date,
        edition=edition,
    )


def fetch_code(
    chapter_prefix: str,
    *,
    id: str,
    title: str,
    short_title: str,
    kind: ActKind = ActKind.CODE,
    number: str | None = None,
    date: str | None = None,
    edition: str | None = None,
    delay: float = 0.2,
    progress: bool = False,
) -> RawAct:
    titles = list_chapter_titles(chapter_prefix)
    parts: list[str] = []
    for i, t in enumerate(titles, 1):
        parts.append(clean_wikitext(fetch_wikitext(t)))
        if progress:
            print(f"  [{i}/{len(titles)}] {t}")
        time.sleep(delay)
    return parse_statute_text(
        "\n".join(parts),
        id=id,
        title=title,
        short_title=short_title,
        kind=kind,
        number=number,
        date=date,
        edition=edition,
    )
