from praxis.tasks import review_contract

_GOOD = """
Договор купли-продажи.
1. Предмет договора: продавец передаёт покупателю товар — ноутбук.
2. Цена товара составляет 60000 руб., оплата в течение 3 дней.
3. Срок передачи товара — не позднее 5 дней с момента оплаты.
4. Ответственность: за просрочку продавец уплачивает неустойку.
5. Изменение и расторжение договора — по соглашению сторон.
6. Реквизиты и подписи сторон, ИНН, адрес.
"""


def _by_label(review, label):
    return next(c for c in review.checks if c.label == label)


def test_good_contract_passes_presence_checks():
    r = review_contract(_GOOD)
    assert r.ok
    assert _by_label(r, "Предмет договора").status == "ok"
    assert _by_label(r, "Цена и порядок оплаты").status == "ok"
    assert _by_label(r, "Сроки исполнения").status == "ok"
    # ссылки на нормы проставлены
    assert _by_label(r, "Предмет договора").source_url == "https://www.zakonrf.info/gk/432/"
    assert r.disclaimer


def test_missing_subject_flagged():
    text = "Стоимость услуг 10000 руб. Срок оказания — 7 дней. Подписи сторон."
    r = review_contract(text)
    assert _by_label(r, "Предмет договора").status == "missing"


def test_risk_clause_flagged():
    text = _GOOD + "\n7. Приобретённый товар возврату не подлежит, претензии не принимаются."
    r = review_contract(text)
    risk = _by_label(r, "Отказ от ответственности или возврата")
    assert risk.status == "warning"
    assert "16 ЗоЗПП" in risk.citation


def test_no_risk_clause_is_ok():
    r = review_contract(_GOOD)
    assert _by_label(r, "Отказ от ответственности или возврата").status == "ok"
    assert _by_label(r, "Навязанная подсудность").status == "ok"


def test_too_short_text_not_reviewed():
    r = review_contract("договор")
    assert not r.ok and r.note


def test_summary_counts_present():
    r = review_contract(_GOOD)
    assert "Проверено пунктов" in r.summary
