"""Реальная выгрузка корпуса кодексов РФ с Викитеки в JSON.

    python scripts/fetch_corpus.py [out_dir=corpus] [коды...]

Без аргументов кодов — выгружает все известные. Результат подключается через
PRAXIS_CORPUS_DIR (см. ingest.corpus.load_corpus_dir).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from praxis.ingest.sources.json_loader import act_to_dict  # noqa: E402
from praxis.ingest.sources.wikisource import fetch_code, fetch_page_act  # noqa: E402

_EDITION = "Викитека (транскрипция; сверять с pravo.gov.ru)"

# Кодексы: id -> (префикс глав на Викитеке, id, полное название, короткое, номер ФЗ, дата)
CODES = {
    "gk": ("Гражданский кодекс РФ/Глава", "gk-rf", "Гражданский кодекс Российской Федерации", "ГК РФ", "51-ФЗ", "1994-11-30"),
    "tk": ("Трудовой кодекс РФ/Глава", "tk-rf", "Трудовой кодекс Российской Федерации", "ТК РФ", "197-ФЗ", "2001-12-30"),
    "nk": ("Налоговый кодекс РФ/Глава", "nk-rf", "Налоговый кодекс Российской Федерации", "НК РФ", "146-ФЗ", "1998-07-31"),
    "uk": ("Уголовный кодекс РФ/Глава", "uk-rf", "Уголовный кодекс Российской Федерации", "УК РФ", "63-ФЗ", "1996-06-13"),
    "koap": ("Кодекс РФ об административных правонарушениях/Глава", "koap-rf", "Кодекс Российской Федерации об административных правонарушениях", "КоАП РФ", "195-ФЗ", "2001-12-30"),
    "zhk": ("Жилищный кодекс РФ/Глава", "zhk-rf", "Жилищный кодекс Российской Федерации", "ЖК РФ", "188-ФЗ", "2004-12-29"),
}

# Одностраничные законы (без глав-подстраниц): id -> (страница Викитеки, id, название, короткое, номер, дата)
LAWS = {
    "zozpp": ("Закон РФ от 07.02.1992 № 2300-I", "zozpp", "Закон РФ «О защите прав потребителей»", "ЗоЗПП", "2300-I", "1992-02-07"),
}


def main() -> None:
    args = sys.argv[1:]
    known = set(CODES) | set(LAWS)
    out = Path(args[0]) if args and args[0] not in known else Path("corpus")
    wanted = [a for a in args if a in known] or list(known)
    out.mkdir(parents=True, exist_ok=True)

    for key in wanted:
        if key in CODES:
            prefix, act_id, title, short, number, date = CODES[key]
            print(f"\nВыгрузка {short} с Викитеки...")
            raw = fetch_code(prefix, id=act_id, title=title, short_title=short,
                             number=number, date=date, edition=_EDITION)
        else:
            page, act_id, title, short, number, date = LAWS[key]
            print(f"\nВыгрузка {short} с Викитеки (одна страница)...")
            raw = fetch_page_act(page, id=act_id, title=title, short_title=short,
                                 number=number, date=date, edition=_EDITION)
        dest = out / f"{act_id}.json"
        dest.write_text(
            json.dumps(act_to_dict(raw), ensure_ascii=False, indent=1), encoding="utf-8"
        )
        n_points = sum(len(a.points) or 1 for a in raw.articles)
        print(f"  {short}: {len(raw.articles)} статей, ~{n_points} норм -> {dest}")


if __name__ == "__main__":
    main()
