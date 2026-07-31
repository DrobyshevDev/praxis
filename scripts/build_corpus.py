"""Сборка JSON-корпуса из официальных plaintext-текстов.

Для каждого <name>.txt (текст акта) рядом лежит <name>.meta.json с реквизитами:
    {"id":"gk-rf-1","kind":"кодекс","title":"...","short_title":"ГК РФ",
     "number":"51-ФЗ","date":"1994-11-30","edition":"..."}

    python scripts/build_corpus.py <src_dir> <out_dir>

Полученный <out_dir> подключается через PRAXIS_CORPUS_DIR (см. load_corpus_dir).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from praxis.core.models import ActKind  # noqa: E402
from praxis.ingest.statute_parser import parse_statute_text  # noqa: E402


def _act_to_dict(raw) -> dict:
    articles = []
    for a in raw.articles:
        item = {"number": a.number, "title": a.title}
        if a.points:
            item["points"] = [list(p) for p in a.points]
        else:
            item["text"] = a.text
        articles.append(item)
    return {
        "id": raw.id,
        "kind": raw.kind.value,
        "title": raw.title,
        "short_title": raw.short_title,
        "number": raw.number,
        "date": raw.date,
        "edition": raw.edition,
        "articles": articles,
    }


def main() -> None:
    if len(sys.argv) != 3:
        print("usage: python scripts/build_corpus.py <src_dir> <out_dir>")
        raise SystemExit(2)

    src, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)

    for txt in sorted(src.glob("*.txt")):
        meta = json.loads((src / f"{txt.stem}.meta.json").read_text(encoding="utf-8"))
        raw = parse_statute_text(
            txt.read_text(encoding="utf-8"),
            id=meta["id"],
            title=meta["title"],
            short_title=meta["short_title"],
            kind=ActKind(meta.get("kind", "кодекс")),
            number=meta.get("number"),
            date=meta.get("date"),
            edition=meta.get("edition"),
        )
        dest = out / f"{raw.id}.json"
        dest.write_text(
            json.dumps(_act_to_dict(raw), ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"{txt.name} -> {dest.name} ({len(raw.articles)} статей)")


if __name__ == "__main__":
    main()
