from decimal import Decimal

import pytest

from tests.autofixture import AutoFixture
from users.models import CashbackHistory
from utils.constants import DEFAULT_AMOUNT


@pytest.mark.django_db
def test_cashback_balance():

    AutoFixture(
        CashbackHistory,
        overrides={
            "amount": Decimal("100.00"),
            "type": CashbackHistory.TypeChoices.EARNED,
        },
    ).create()

    assert CashbackHistory.objects.cashback_balance() == Decimal("100.00")

    AutoFixture(
        CashbackHistory,
        overrides={
            "amount": Decimal("100.00"),
            "type": CashbackHistory.TypeChoices.SPENT,
        },
    ).create()

    assert CashbackHistory.objects.cashback_balance() == DEFAULT_AMOUNT

    released = AutoFixture(
        CashbackHistory,
        overrides={
            "amount": Decimal("100.00"),
            "type": CashbackHistory.TypeChoices.RELEASED,
        },
    ).create()

    assert CashbackHistory.objects.cashback_balance() == Decimal("100.00")

    AutoFixture(
        CashbackHistory,
        overrides={
            "amount": Decimal("100.00"),
            "type": CashbackHistory.TypeChoices.RESERVED,
            "released_with": released,
        },
    ).create()

    assert CashbackHistory.objects.cashback_balance() == DEFAULT_AMOUNT
