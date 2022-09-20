from datetime import date, timedelta

import pytest
from django.contrib.auth.models import Permission

from portal.account.models import User
from portal.document.models import Document
from portal.investment.models import Investment, Item
from portal.provider.models import Provider, Segment
from portal.vehicle.models import Category, Vehicle


@pytest.fixture
def permission_manage_investments():
    return Permission.objects.get(codename="manage_investments")


@pytest.fixture
def permission_manage_items():
    return Permission.objects.get(codename="manage_items")


@pytest.fixture
def permission_manage_segments():
    return Permission.objects.get(codename="manage_segments")


@pytest.fixture
def permission_manage_providers():
    return Permission.objects.get(codename="manage_providers")


@pytest.fixture
def permission_manage_categories():
    return Permission.objects.get(codename="manage_categories")


@pytest.fixture
def permission_manage_vehicles():
    return Permission.objects.get(codename="manage_vehicles")


@pytest.fixture
def user():
    user = User.objects.create_user(  # type: ignore
        email="test@example.com",
        password="password",
        first_name="Leslie",
        last_name="Wade",
    )
    user._password = "password"
    return user


@pytest.fixture
def staff_user():
    user = User.objects.create_user(  # type: ignore
        email="test@example.com",
        password="password",
        first_name="Leslie",
        last_name="Wade",
        is_staff=True,
    )
    user._password = "password"
    user.user_permissions.add(*Permission.objects.all())
    return user


@pytest.fixture
def segment():
    return Segment.objects.create(name="Comunicação Visual")


@pytest.fixture
def category():
    return Category.objects.create(name="Jornal Impresso")


@pytest.fixture
def vehicle(category):
    vehicle = Vehicle.objects.create(name="Correio Sudoeste", category=category)
    return vehicle


@pytest.fixture
def published_vehicle(category):
    vehicle = Vehicle.objects.create(
        name="Jornal da Região", category=category, is_published=True
    )
    return vehicle


@pytest.fixture
def published_vehicle_with_date(category):
    vehicle = Vehicle.objects.create(
        name="Jornal Jogo Sério",
        category=category,
        is_published=True,
        publication_date=(date.today() + timedelta(days=1)),
    )
    return vehicle


@pytest.fixture
def provider(segment):
    provider = Provider.objects.create(name="Visualize Comunicação", segment=segment)
    Document.objects.bulk_create(
        [
            Document(name="Documento 01", provider=provider),
            Document(name="Documento 02", provider=provider),
        ]
    )
    return provider


@pytest.fixture
def published_provider(segment):
    provider = Provider.objects.create(
        name="Agência 123", segment=segment, is_published=True
    )
    return provider


@pytest.fixture
def document(provider):
    document = Document.objects.create(
        name="Contrato de Serviço", provider=provider, file="/path/to/myfile.pdf"
    )
    return document


@pytest.fixture
def investment():
    return Investment.objects.create(year=2022, month=3, is_published=False)


@pytest.fixture
def published_investment():
    return Investment.objects.create(year=2022, month=2, is_published=True)


@pytest.fixture
def investment_with_items():
    investment = Investment.objects.create(year=2022, month=1)
    Item.objects.create(name="TV", slug="tv", value=100, investment=investment),
    Item.objects.create(name="Radio", slug="radio", value=100, investment=investment),
    Item.objects.create(
        name="Internet", slug="internet", value=200, investment=investment
    )
    return investment
