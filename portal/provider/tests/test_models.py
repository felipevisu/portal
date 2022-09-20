import pytest
from django.template.defaultfilters import slugify

pytestmark = pytest.mark.django_db


def test_segment(segment):
    assert segment.slug == slugify("Comunicação Visual")


def test_provider(provider):
    assert provider.slug == slugify("Visualize Comunicação")
    assert provider.documents.count() == 2


def test_document(document):
    assert document.extension() == ".pdf"
