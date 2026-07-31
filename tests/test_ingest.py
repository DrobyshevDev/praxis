from praxis.core.models import Provision
from praxis.ingest import build_provisions, load_sample_provisions
from praxis.ingest.schema import RawAct, RawArticle
from praxis.core.models import ActKind


def test_sample_loads_nonempty():
    provisions = load_sample_provisions()
    assert provisions
    assert all(isinstance(p, Provision) for p in provisions)
    assert all(p.text.strip() for p in provisions)


def test_citation_format():
    provisions = load_sample_provisions()
    p431 = next(p for p in provisions if p.article_number == "431" and "1" in p.path)
    assert p431.citation == "ст. 431 ГК РФ, ч. 1"


def test_article_without_points_becomes_single_provision():
    raw = RawAct(
        id="test",
        kind=ActKind.CODE,
        title="Тест",
        short_title="ТК",
        articles=[RawArticle(number="1", title="Одна", text="Текст нормы.")],
    )
    provisions = build_provisions(raw)
    assert len(provisions) == 1
    assert provisions[0].path == ""
    assert provisions[0].citation == "ст. 1 ТК"


def test_points_expand_to_multiple_provisions():
    raw = RawAct(
        id="test",
        kind=ActKind.CODE,
        title="Тест",
        short_title="ТК",
        articles=[
            RawArticle(
                number="5",
                title="С пунктами",
                points=[("п. 1", "Первый."), ("п. 2", "Второй.")],
            )
        ],
    )
    provisions = build_provisions(raw)
    assert [p.path for p in provisions] == ["п. 1", "п. 2"]
    assert provisions[0].id == "test:5:1"
    assert {p.position for p in provisions} == {0, 1}
