"""Оффлайн-тест очистки вики-разметки (без обращения к сети)."""

from praxis.ingest.chunker import build_provisions
from praxis.ingest.sources.wikisource import clean_wikitext
from praxis.ingest.statute_parser import parse_statute_text

_WIKITEXT = """===== Статья 431. Толкование договора =====
{{якорь|Статья 431}}При толковании условий договора судом принимается во внимание [[буквальное значение]] содержащихся в нём слов и выражений.<ref>примечание</ref>

(в ред. Федерального закона от 08.03.2015 № 42-ФЗ)

===== Статья 432. Основные положения о заключении договора =====
{{якорь|Статья 432. Пункт 1}}1. Договор считается заключённым, если между сторонами достигнуто [[соглашение|соглашение сторон]].
{{якорь|Статья 432. Пункт 2}}2. Договор заключается посредством направления оферты.
"""


def test_clean_removes_markup():
    text = clean_wikitext(_WIKITEXT)
    assert "{{" not in text and "}}" not in text
    assert "[[" not in text and "]]" not in text
    assert "<ref>" not in text
    assert "=====" not in text
    assert "в ред." not in text  # аннотация редакции убрана
    assert "буквальное значение" in text  # текст ссылки сохранён
    assert "соглашение сторон" in text  # подпись ссылки [[t|подпись]]


def test_clean_then_parse_yields_provisions():
    raw = parse_statute_text(
        clean_wikitext(_WIKITEXT), id="gk-rf", title="ГК РФ", short_title="ГК РФ"
    )
    provisions = build_provisions(raw)
    assert any(p.citation == "ст. 431 ГК РФ" for p in provisions)
    p432 = [p for p in provisions if p.article_number == "432"]
    assert {p.path for p in p432} == {"п. 1", "п. 2"}
