#!/usr/bin/env python3
"""Числа, которыми praxis описывает свой корпус, сходятся с самим корпусом.

«1712 статей, 4717 норм» написано девять раз — в обоих README, на обеих
страницах документации, цифрами с разделителем тысяч и без. «Шесть кодексов» —
ещё дважды. Ни одно из этих мест не открывает `corpus/`, и разойтись они могут
молча: добавить кодекс или перевыгрузить ГК — ровно тот коммит, после которого
все девять неверны, и никто об этом не узнает, пока не пересчитает руками.

Считается здесь один раз и **тем же кодом, что и сам praxis**:
`load_corpus_dir` плюс `build_provisions`. Это важнее, чем кажется. Наивный
подсчёт по JSON даёт для ГК 4297 норм, а не 4717, потому что статья без
разбиения на пункты — это тоже одна норма, и знает об этом чанкер, а не файл.
Проверка, считающая по-своему, ловила бы собственную арифметику.

Пропавшее утверждение — тоже расхождение. Если фразу перепишут так, что шаблон
перестанет находиться, проверка перестанет проверять и промолчит об этом.

    python scripts/check_corpus_claims.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

#: Где искать корпус. Каталог в репозитории, а не PRAXIS_CORPUS_DIR: проверяется
#: то, что лежит здесь и что описывают эти файлы, а не то, что подсунуто в
#: окружении.
CORPUS = ROOT / "corpus"

#: Слова для количества кодексов. Диапазон узкий намеренно: корпус из двадцати
#: кодексов — другой продукт, и падение проверки на нём правильно.
RU_WORDS = {1: "один", 2: "два", 3: "три", 4: "четыре", 5: "пять", 6: "шесть",
            7: "семь", 8: "восемь", 9: "девять", 10: "десять"}
EN_WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six",
            7: "seven", 8: "eight", 9: "nine", 10: "ten"}


def grouped(n: int) -> str:
    """4717 как в английском тексте: 4,717."""
    return f"{n:,}"


def measured() -> dict[str, int]:
    from praxis.cases import load_practice
    from praxis.ingest import build_provisions
    from praxis.ingest.corpus import load_corpus_dir

    acts = load_corpus_dir(CORPUS)
    codes = [a for a in acts if str(getattr(a, "kind", "")).endswith("CODE")]
    civil = next((a for a in acts if "ГК" in (a.short_title or a.title)), None)
    if civil is None:
        raise SystemExit("  в корпусе нет ГК РФ — считать нечего")

    import os

    previous = os.environ.get("PRAXIS_CORPUS_DIR")
    os.environ["PRAXIS_CORPUS_DIR"] = str(CORPUS)
    try:
        practice = len(load_practice())
    finally:
        if previous is None:
            os.environ.pop("PRAXIS_CORPUS_DIR", None)
        else:
            os.environ["PRAXIS_CORPUS_DIR"] = previous

    return {
        "acts": len(acts),
        "codes": len(codes),
        "civil_articles": len(civil.articles),
        "civil_provisions": len(build_provisions(civil)),
        "practice": practice,
    }


def main() -> int:
    truth = measured()
    articles, provisions = truth["civil_articles"], truth["civil_provisions"]
    codes = truth["codes"]
    problems: list[str] = []
    checked = 0

    def want(where: str, pattern: str, shape: str) -> None:
        nonlocal checked
        checked += 1
        text = (ROOT / where).read_text(encoding="utf-8")
        if re.search(pattern, text) is None:
            problems.append(f"{where}: ждали «{shape}» — не сходится или фразу переписали")

    ru_count, en_count = RU_WORDS.get(codes), EN_WORDS.get(codes)
    if ru_count is None or en_count is None:
        problems.append(f"кодексов {codes} — для такого числа у скрипта нет слова")
    else:
        want("README.md", rf"(?i){ru_count} кодекс\w*", f"{ru_count} кодексов")
        want("README.en.md", rf"(?i){en_count} codes", f"{en_count.title()} codes")

    # Русские тексты — без разделителя тысяч, английские — с ним.
    want("README.md", rf"{articles} стат\w+, {provisions} норм",
         f"{articles} статей, {provisions} норм")
    want("README.md", rf"\({provisions} норм", f"({provisions} норм")
    want("docs/index.md", rf"{articles} стат\w+, {provisions} норм",
         f"{articles} статей, {provisions} норм")
    want("docs/index.md", rf"\({provisions} норм", f"({provisions} норм")

    want("README.en.md", rf"{grouped(articles)} articles, {grouped(provisions)} provisions",
         f"{grouped(articles)} articles, {grouped(provisions)} provisions")
    want("README.en.md", rf"\({grouped(provisions)} provisions",
         f"({grouped(provisions)} provisions")
    want("docs/index.en.md", rf"{grouped(articles)} articles, {grouped(provisions)}",
         f"{grouped(articles)} articles, {grouped(provisions)}")
    want("docs/index.en.md", rf"\({grouped(provisions)} provisions",
         f"({grouped(provisions)} provisions")

    for problem in problems:
        print(f"  {problem}")
    if problems:
        print(f"\n  расхождений: {len(problems)}", file=sys.stderr)
        return 1

    print(
        f"  {truth['acts']} актов ({codes} кодексов), ГК — {articles} статей и "
        f"{provisions} норм, практики {truth['practice']} пунктов Пленума; "
        f"{checked} утверждений в документации говорят то же."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
