import pytest
from django.contrib.auth.models import Permission

from portal.account.models import User
from portal.document.models import Document, DocumentFile
from portal.entry import EntryType
from portal.entry.models import Category, Entry
from portal.investment.models import Investment, Item


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
def permission_manage_entries():
    return Permission.objects.get(codename="manage_entries")


@pytest.fixture
def user():
    user = User.objects.create_user(  # type: ignore
        email="test@example.com",
        password="password",
        first_name="Felipe",
        last_name="Faria",
    )
    user._password = "password"
    return user


@pytest.fixture
def staff_user():
    user = User.objects.create_user(  # type: ignore
        email="test@example.com",
        password="password",
        first_name="Vinícius",
        last_name="Gonçalves",
        is_staff=True,
    )
    user._password = "password"
    user.user_permissions.add(*Permission.objects.all())
    return user


@pytest.fixture
def category():
    return Category.objects.create(name="Category 1", slug="category-1")


@pytest.fixture
def vehicle(category):
    vehicle = Entry.objects.create(
        name="Vehicle",
        slug="vehicle",
        type=EntryType.VEHICLE,
        document_number="123456789",
        category=category,
        is_published=True,
    )
    return vehicle


@pytest.fixture
def unpublished_vehicle(category):
    vehicle = Entry.objects.create(
        name="Unpublished vehicle",
        slug="unpublished-vehicle",
        type=EntryType.VEHICLE,
        document_number="123456789",
        category=category,
        is_published=False,
    )
    return vehicle


@pytest.fixture
def provider(category):
    provider = Entry.objects.create(
        name="Provider",
        slug="provider",
        type=EntryType.PROVIDER,
        document_number="123456789",
        category=category,
        is_published=True,
    )
    return provider


@pytest.fixture
def unpublished_vehicle(category):
    provider = Entry.objects.create(
        name="Unpublished provider",
        slug="unpublished-provider",
        type=EntryType.PROVIDER,
        document_number="123456789",
        category=category,
        is_published=False,
    )
    return provider


@pytest.fixture
def default_file():
    document_file = DocumentFile.objects.create(file="/path/to/file.pdf")
    return document_file


@pytest.fixture
def document_from_provider(provider, default_file):
    document = Document.objects.create(
        name="Contrato de Serviço", entry=provider, default_file=default_file
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
