from praxis.core.models import Act, ActKind, Answer, Citation, Provision
from praxis.tasks import build_lawsuit

ZOZPP = Act(id="zozpp", kind=ActKind.FEDERAL_LAW, title="Закон о защите прав потребителей",
            short_title="ЗоЗПП", number="2300-I", date="1992-02-07")
GK = Act(id="gk-rf", kind=ActKind.CODE, title="Гражданский кодекс", short_title="ГК РФ")
UK = Act(id="uk-rf", kind=ActKind.CODE, title="Уголовный кодекс", short_title="УК РФ")


def _answer(act, num, title, text):
    p = Provision(id=f"{act.id}:{num}", act=act, article_number=num, article_title=title,
                  path="", text=text, position=0)
    return Answer(question="q", text="t", citations=[Citation(p)], confidence=0.7)


def test_consumer_lawsuit_built_and_grounded():
    ans = _answer(ZOZPP, "18", "Права потребителя при недостатках товара",
                  "Потребитель вправе потребовать возврата уплаченной суммы.")
    res = build_lawsuit(ans)
    assert res.applicable
    assert "ИСКОВОЕ ЗАЯВЛЕНИЕ" in res.text
    assert "ПРОШУ СУД" in res.text
    assert "ст. 18 ЗоЗПП" in res.text  # обоснование цитирует норму
    # потребительские требования: неустойка, моральный вред, штраф 50%
    assert "ст. 23" in res.text and "ст. 15" in res.text and "50%" in res.text
    # льгота по госпошлине и подсудность по месту истца
    assert "333.36" in res.text and "17" in res.text
    assert res.based_on == ["ст. 18 ЗоЗПП"]


def test_general_civil_lawsuit_uses_395():
    ans = _answer(GK, "395", "Проценты за пользование чужими средствами",
                  "За пользование чужими денежными средствами подлежат уплате проценты.")
    res = build_lawsuit(ans)
    assert res.applicable
    assert "ст. 395 ГК РФ" in res.text
    assert "ст. 28 ГПК" in res.text  # подсудность по месту ответчика
    assert "50%" not in res.text  # не потребительский — без штрафа ЗоЗПП


def test_lawsuit_not_applicable_for_criminal():
    ans = _answer(UK, "159", "Мошенничество", "Мошенничество, то есть хищение...")
    res = build_lawsuit(ans)
    assert not res.applicable
    assert "УК РФ" in res.note and res.text == ""


def test_lawsuit_no_citations():
    res = build_lawsuit(Answer(question="q", text="t", citations=[]))
    assert not res.applicable and res.note
