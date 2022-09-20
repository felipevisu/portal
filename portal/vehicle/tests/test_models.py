import pytest
from django.template.defaultfilters import slugify

pytestmark = pytest.mark.django_db


def test_category(category):
    assert category.slug == slugify("Jornal Impresso")


def test_vehicle(vehicle):
    assert vehicle.slug == slugify("Correio Sudoeste")


def test_vehicle_publication(vehicle, published_vehicle, published_vehicle_with_date):
    assert not vehicle.is_visible
    assert not published_vehicle_with_date.is_visible
    assert published_vehicle.is_visible
