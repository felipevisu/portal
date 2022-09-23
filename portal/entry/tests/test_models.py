import pytest
from django.template.defaultfilters import slugify

pytestmark = pytest.mark.django_db


def test_category(category):
    assert category.slug == slugify("Jornal Impresso")


def test_entry(entry):
    assert entry.slug == slugify("Correio Sudoeste")


def test_entry_publication(entry, published_entry, published_entry_with_date):
    assert not entry.is_visible
    assert not published_entry_with_date.is_visible
    assert published_entry.is_visible
