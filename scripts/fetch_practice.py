"""Выгрузка судебной практики (Пленумы ВС РФ) с Викитеки в corpus/practice.json.

    python scripts/fetch_practice.py [out_dir=corpus]

Подключается через PRAXIS_CORPUS_DIR (см. cases.load_practice).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from praxis.cases.wikisource import fetch_practice  # noqa: E402


def main() -> None:
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "corpus")
    out.mkdir(parents=True, exist_ok=True)

    cases = fetch_practice()
    data = [
        {
            "id": c.id,
            "court": c.court,
            "number": c.number,
            "date": c.date,
            "summary": c.summary,
            "act_id": c.act_id,
            "cited_articles": sorted(c.cited_articles, key=lambda x: int(x) if x.isdigit() else 0),
        }
        for c in cases
    ]
    dest = out / "practice.json"
    dest.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")

    from collections import Counter

    by_act = Counter(c.act_id for c in cases)
    print(f"Пунктов практики: {len(cases)} | по актам: {dict(by_act)}")
    print(f"-> {dest}")


if __name__ == "__main__":
    main()
