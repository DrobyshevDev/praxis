from praxis.core.models import Act, ActKind, Answer, Citation, Provision
from praxis.tasks import build_claim, claim_applicable

ZOZPP = Act(id="zozpp", kind=ActKind.FEDERAL_LAW, title="Закон о защите прав потребителей",
            short_title="ЗоЗПП", number="2300-I", date="1992-02-07")
UK = Act(id="uk-rf", kind=ActKind.CODE, title="Уголовный кодекс", short_title="УК РФ")


def _answer(act, num, title, text):
    p = Provision(id=f"{act.id}:{num}", act=act, article_number=num, article_title=title,
                  path="", text=text, position=0)
    return Answer(question="q", text="t", citations=[Citation(p)], confidence=0.7)


def test_consumer_claim_is_built_and_grounded():
    ans = _answer(ZOZPP, "18", "Права потребителя при обнаружении недостатков",
                  "Потребитель вправе потребовать замены товара либо возврата уплаченной суммы.")
    assert claim_applicable(ans)
    res = build_claim(ans)
    assert res.applicable
    assert "ПРЕТЕНЗИЯ" in res.text
    # обоснование цитирует реальную норму
    assert "ст. 18 ЗоЗПП" in res.text
    assert "замены товара" in res.text  # дословный фрагмент нормы
    # потребительские последствия (неустойка/штраф/моральный вред)
    assert "ст. 23" in res.text and "ст. 15" in res.text
    assert res.based_on == ["ст. 18 ЗоЗПП"]
    assert res.disclaimer


def test_claim_not_applicable_for_criminal_question():
    ans = _answer(UK, "159", "Мошенничество", "Мошенничество, то есть хищение...")
    assert not claim_applicable(ans)
    res = build_claim(ans)
    assert not res.applicable
    assert "УК РФ" in res.note
    assert res.text == ""


def test_claim_no_citations():
    res = build_claim(Answer(question="q", text="t", citations=[]))
    assert not res.applicable
    assert res.note


def test_long_norm_text_is_trimmed_in_grounds():
    long_text = "Норма. " + "слово " * 200
    ans = _answer(ZOZPP, "22", "Сроки", long_text)
    res = build_claim(ans)
    assert "…" in res.text  # длинная норма обрезана в обосновании
