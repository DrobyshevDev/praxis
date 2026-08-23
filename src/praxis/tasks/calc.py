"""Правовые калькуляторы: неустойка (ЗоЗПП) и госпошлина в суд (НК РФ).

Детерминированные расчёты с опорой на норму: каждый результат несёт ссылку на
статью-основание и заметку о редакции. Ставки и шкала сверены с действующей
редакцией (zakonrf.info) на момент реализации — при изменении закона правятся
здесь, в одном месте.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..sources import verify_url


@dataclass
class CalcBasis:
    citation: str
    source_url: str | None
    note: str = ""


@dataclass
class PenaltyResult:
    amount: float  # итоговая неустойка, ₽
    per_day: float  # за один день, ₽
    days: int
    rate_pct: float  # ставка, % в день
    capped: bool  # упёрлась в потолок (для услуг — цена услуги)
    basis: CalcBasis
    breakdown: str


@dataclass
class FeeResult:
    fee: float  # госпошлина, ₽
    exempt: bool  # потребитель освобождён (иск ≤ 1 млн)
    basis: CalcBasis
    breakdown: str


@dataclass
class InterestResult:
    amount: float  # проценты, ₽
    basis: CalcBasis
    breakdown: str


def _rub(x: float) -> float:
    """Госпошлина исчисляется в полных рублях (НК ст. 52 п. 6)."""
    return float(int(x + 0.5))


# --- Неустойка по Закону о защите прав потребителей -------------------------

def penalty(price: float, days: int, kind: str = "товар") -> PenaltyResult:
    """Неустойка потребителю за просрочку.

    Товар — 1% цены за каждый день (ст. 23 ЗоЗПП), без установленного законом
    потолка. Работа/услуга — 3% цены за каждый день (ст. 28 п. 5 ЗоЗПП), но общая
    сумма неустойки не может превышать цену работы (услуги).
    """
    if price <= 0:
        raise ValueError("Цена должна быть больше нуля")
    if days < 0:
        raise ValueError("Число дней не может быть отрицательным")

    is_service = kind in ("услуга", "работа", "service")
    rate = 0.03 if is_service else 0.01
    per_day = price * rate
    amount = per_day * days
    capped = False
    if is_service and amount > price:
        amount, capped = price, True

    if is_service:
        basis = CalcBasis(
            "ст. 28 ЗоЗПП, п. 5", verify_url("zozpp", "28"),
            "3% цены за день; сумма неустойки не превышает цену работы (услуги).",
        )
    else:
        basis = CalcBasis(
            "ст. 23 ЗоЗПП", verify_url("zozpp", "23"),
            "1% цены товара за каждый день просрочки.",
        )
    bd = f"{price:,.0f} ₽ × {rate * 100:.0f}% × {days} дн. = {per_day:,.0f} ₽/день"
    if capped:
        bd += f"; ограничено ценой услуги — {price:,.0f} ₽"
    return PenaltyResult(
        amount=round(amount, 2), per_day=round(per_day, 2), days=days,
        rate_pct=rate * 100, capped=capped, basis=basis, breakdown=bd.replace(",", " "),
    )


# --- Проценты за пользование чужими средствами (ст. 395 ГК) ------------------

def interest_395(principal: float, rate_pct: float, days: int) -> InterestResult:
    """Проценты по ст. 395 ГК за один период с неизменной ставкой.

    Ставку (ключевую ставку Банка России) вводит пользователь: она регулярно
    меняется, поэтому не зашита в код — иначе расчёт молча устаревал бы. Формула:
    сумма × ставка × дни / 365. Если за время просрочки ставка менялась,
    посчитайте по каждому периоду отдельно и сложите.
    """
    if principal <= 0:
        raise ValueError("Сумма долга должна быть больше нуля")
    if rate_pct < 0:
        raise ValueError("Ставка не может быть отрицательной")
    if days < 0:
        raise ValueError("Число дней не может быть отрицательным")

    amount = principal * (rate_pct / 100) * days / 365
    basis = CalcBasis(
        "ст. 395 ГК РФ", verify_url("gk-rf", "395"),
        "Ставка — ключевая ставка Банка России (cbr.ru) за период просрочки. При смене "
        "ставки считайте по каждому периоду и складывайте.",
    )
    bd = f"{principal:,.0f} ₽ × {rate_pct:g}% × {days} дн. / 365 = {amount:,.2f} ₽".replace(",", " ")
    return InterestResult(amount=round(amount, 2), basis=basis, breakdown=bd)


# --- Госпошлина в суд общей юрисдикции (имущественный иск) -------------------
# ст. 333.19 НК РФ, ред. 259-ФЗ (действует с 09.09.2024): (нижняя граница, база, ставка)
_FEE_TIERS = [
    (0, 4000, 0.0),
    (100_000, 4000, 0.03),
    (300_000, 10_000, 0.025),
    (500_000, 15_000, 0.02),
    (1_000_000, 25_000, 0.01),
    (3_000_000, 45_000, 0.007),
    (8_000_000, 80_000, 0.0035),
    (24_000_000, 136_000, 0.003),
    (50_000_000, 214_000, 0.002),
    (100_000_000, 314_000, 0.0015),
]
_FEE_CAP = 900_000  # верхний предел пошлины


def _fee_soj(amount: float) -> float:
    """Госпошлина по ст. 333.19 НК для имущественного иска в СОЮ (без льгот)."""
    low, base, rate = _FEE_TIERS[0]
    for lb, b, r in _FEE_TIERS:
        if amount > lb:
            low, base, rate = lb, b, r
        else:
            break
    fee = base + rate * (amount - low)
    return _rub(min(fee, _FEE_CAP))


def court_fee(claim_amount: float, consumer: bool = False) -> FeeResult:
    """Госпошлина при подаче имущественного иска в суд общей юрисдикции.

    consumer=True — иск о защите прав потребителей: при цене иска до 1 000 000 ₽
    истец освобождён от пошлины (ст. 333.36 НК, ст. 17 ЗоЗПП); свыше — платит
    пошлину по ст. 333.19, уменьшенную на пошлину с 1 000 000 ₽.
    """
    if claim_amount < 0:
        raise ValueError("Цена иска не может быть отрицательной")

    if consumer:
        threshold = 1_000_000
        if claim_amount <= threshold:
            return FeeResult(
                0.0, True,
                CalcBasis("ст. 333.36 НК РФ, п. 3", verify_url("nk-rf", "333.36"),
                          "Потребитель освобождён от госпошлины при цене иска до 1 000 000 ₽."),
                "Иск о защите прав потребителей до 1 000 000 ₽ — госпошлина не уплачивается.",
            )
        fee = _rub(_fee_soj(claim_amount) - _fee_soj(threshold))
        return FeeResult(
            fee, False,
            CalcBasis("ст. 333.19, 333.36 НК РФ", verify_url("nk-rf", "333.19"),
                      "Редакция 259-ФЗ (с 09.09.2024). Свыше 1 млн — пошлина по ст. 333.19 "
                      "за вычетом пошлины с 1 000 000 ₽."),
            f"пошлина с {claim_amount:,.0f} ₽ − пошлина с 1 000 000 ₽ = {fee:,.0f} ₽".replace(",", " "),
        )

    fee = _fee_soj(claim_amount)
    return FeeResult(
        fee, False,
        CalcBasis("ст. 333.19 НК РФ, п. 1", verify_url("nk-rf", "333.19"),
                  "Имущественный иск в суд общей юрисдикции; редакция 259-ФЗ (с 09.09.2024)."),
        f"по шкале ст. 333.19 для цены иска {claim_amount:,.0f} ₽ = {fee:,.0f} ₽".replace(",", " "),
    )
