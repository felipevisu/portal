import pytest

from ..models import Investment

pytestmark = pytest.mark.django_db


def test_create_investment(investment):
    with pytest.raises(Exception):
        Investment.objects.create(year=2022, mounth=3)


def test_investments_order():
    investment_1 = Investment.objects.create(year=2022, mounth=3)
    investment_2 = Investment.objects.create(year=2021, mounth=12)
    investment_3 = Investment.objects.create(year=2022, mounth=1)

    investment_list = Investment.objects.all()

    assert investment_list[0] == investment_1
    assert investment_list[1] == investment_3
    assert investment_list[2] == investment_2
