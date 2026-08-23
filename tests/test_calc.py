import pytest

from praxis.tasks import court_fee, interest_395, penalty


# --- Неустойка --------------------------------------------------------------

def test_penalty_goods_one_percent():
    r = penalty(50_000, 10, kind="товар")
    assert r.per_day == 500  # 1% от 50 000
    assert r.amount == 5_000
    assert not r.capped
    assert "ст. 23 ЗоЗПП" in r.basis.citation
    assert r.basis.source_url == "https://www.zakonrf.info/zozpp/23/"


def test_penalty_service_three_percent():
    r = penalty(10_000, 5, kind="услуга")
    assert r.per_day == 300  # 3% от 10 000
    assert r.amount == 1_500
    assert not r.capped
    assert "ст. 28 ЗоЗПП" in r.basis.citation


def test_penalty_service_capped_at_price():
    r = penalty(10_000, 40, kind="услуга")  # 300*40 = 12 000 > 10 000
    assert r.amount == 10_000
    assert r.capped


def test_penalty_rejects_bad_input():
    with pytest.raises(ValueError):
        penalty(0, 5)
    with pytest.raises(ValueError):
        penalty(1000, -1)


# --- Госпошлина (ст. 333.19 НК, ред. 259-ФЗ) --------------------------------
# Значения сверены с действующей редакцией на zakonrf.info.

@pytest.mark.parametrize("amount,expected", [
    (100_000, 4_000),
    (250_000, 8_500),     # 4000 + 3%*(150000) — пример с zakonrf
    (300_000, 10_000),
    (500_000, 15_000),
    (1_000_000, 25_000),
    (1_500_000, 30_000),  # 25000 + 1%*(500000)
    (3_000_000, 45_000),
    (200_000_000, 464_000),  # 314000 + 0.15%*(100M)
])
def test_court_fee_tiers(amount, expected):
    assert court_fee(amount).fee == expected


def test_court_fee_upper_cap():
    # 314000 + 0.15%*(900M) = 1 664 000 -> потолок 900 000
    assert court_fee(1_000_000_000).fee == 900_000


def test_consumer_exempt_up_to_1m():
    r = court_fee(500_000, consumer=True)
    assert r.exempt and r.fee == 0
    assert "333.36" in r.basis.citation


def test_consumer_over_1m_pays_difference():
    # свыше 1 млн: fee(1.5M) - fee(1M) = 30000 - 25000 = 5000
    r = court_fee(1_500_000, consumer=True)
    assert not r.exempt
    assert r.fee == 5_000


def test_court_fee_rejects_negative():
    with pytest.raises(ValueError):
        court_fee(-1)


# --- Проценты по ст. 395 ГК -------------------------------------------------

def test_interest_395_basic():
    # 100 000 × 16% × 365/365 = 16 000
    r = interest_395(100_000, 16, 365)
    assert r.amount == 16_000
    assert "ст. 395 ГК РФ" in r.basis.citation
    assert r.basis.source_url == "https://www.zakonrf.info/gk/395/"


def test_interest_395_partial_period():
    # 200 000 × 10% × 30/365 = 1643.84
    r = interest_395(200_000, 10, 30)
    assert r.amount == round(200_000 * 0.10 * 30 / 365, 2)


def test_interest_395_zero_days():
    assert interest_395(50_000, 16, 0).amount == 0


def test_interest_395_rejects_bad_input():
    with pytest.raises(ValueError):
        interest_395(0, 16, 30)
    with pytest.raises(ValueError):
        interest_395(1000, -1, 30)
