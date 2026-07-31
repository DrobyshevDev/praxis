from praxis.core.models import ActKind
from praxis.ingest import build_provisions, load_act_json, parse_statute_text
from praxis.ingest.sources.json_loader import act_from_dict

_SAMPLE_TEXT = """Статья 421. Свобода договора
1. Граждане и юридические лица свободны в заключении договора.
Понуждение к заключению договора не допускается.
4. Условия договора определяются по усмотрению сторон.
Статья 431. Толкование договора
При толковании условий договора судом принимается во внимание буквальное значение слов.
"""


def test_parse_statute_text_articles_and_points():
    raw = parse_statute_text(
        _SAMPLE_TEXT, id="gk-rf-1", title="ГК РФ ч.1", short_title="ГК РФ"
    )
    assert [a.number for a in raw.articles] == ["421", "431"]

    art_421 = raw.articles[0]
    assert [p[0] for p in art_421.points] == ["п. 1", "п. 4"]
    # Многострочный пункт склеен.
    assert "Понуждение" in art_421.points[0][1]

    art_431 = raw.articles[1]
    assert art_431.points == []
    assert art_431.text and "буквальное значение" in art_431.text


def test_parsed_act_builds_provisions_with_citations():
    raw = parse_statute_text(
        _SAMPLE_TEXT, id="gk-rf-1", title="ГК РФ ч.1", short_title="ГК РФ"
    )
    provisions = build_provisions(raw)
    assert any(p.citation == "ст. 421 ГК РФ, п. 4" for p in provisions)


def test_json_loader_round_trip():
    data = {
        "id": "nk-rf-1",
        "kind": "кодекс",
        "title": "Налоговый кодекс РФ (часть первая)",
        "short_title": "НК РФ",
        "articles": [
            {"number": "3", "title": "Основные начала", "text": "Каждое лицо должно уплачивать законно установленные налоги."},
        ],
    }
    raw = act_from_dict(data)
    assert raw.kind == ActKind.CODE
    provisions = build_provisions(raw)
    assert provisions[0].citation == "ст. 3 НК РФ"


def test_load_act_json_from_file(tmp_path):
    import json

    p = tmp_path / "act.json"
    p.write_text(
        json.dumps(
            {
                "id": "tk-rf",
                "kind": "кодекс",
                "title": "Трудовой кодекс",
                "short_title": "ТК РФ",
                "articles": [{"number": "1", "title": "Цели", "points": [["п. 1", "Текст."]]}],
            }
        ),
        encoding="utf-8",
    )
    raw = load_act_json(p)
    assert raw.short_title == "ТК РФ"
    assert build_provisions(raw)[0].citation == "ст. 1 ТК РФ, п. 1"
