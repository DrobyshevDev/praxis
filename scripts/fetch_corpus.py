"""Реальная выгрузка корпуса ГК РФ с Викитеки в JSON.

    python scripts/fetch_corpus.py [out_dir=corpus]

Результат подключается через PRAXIS_CORPUS_DIR (см. ingest.corpus.load_corpus_dir).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from praxis.ingest.sources.json_loader import act_to_dict  # noqa: E402
from praxis.ingest.sources.wikisource import fetch_code  # noqa: E402


def main() -> None:
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "corpus")
    out.mkdir(parents=True, exist_ok=True)

    print("Выгрузка ГК РФ (части 1-3) с Викитеки...")
    raw = fetch_code(
        "Гражданский кодекс РФ/Глава",
        id="gk-rf",
        title="Гражданский кодекс Российской Федерации",
        short_title="ГК РФ",
        number="51-ФЗ",
        date="1994-11-30",
        edition="Викитека (транскрипция; сверять с pravo.gov.ru)",
        progress=True,
    )
    dest = out / "gk-rf.json"
    dest.write_text(
        json.dumps(act_to_dict(raw), ensure_ascii=False, indent=1), encoding="utf-8"
    )
    n_points = sum(len(a.points) or 1 for a in raw.articles)
    print(f"\nГК РФ: {len(raw.articles)} статей, ~{n_points} норм -> {dest}")


if __name__ == "__main__":
    main()
