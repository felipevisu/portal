import pytest
from django.contrib.auth.models import Permission

from portal.account.models import User
from portal.channel.models import Channel
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
def permission_manage_plugins():
    return Permission.objects.get(codename="manage_plugins")


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
    return user


@pytest.fixture
def admin_user(db):
    """Return a Django admin user."""
    return User.objects.create_user(
        "admin@example.com",
        "password",
        is_staff=True,
        is_active=True,
        is_superuser=True,
    )


@pytest.fixture
def category():
    return Category.objects.create(name="Category", slug="category")


@pytest.fixture
def category_list():
    categories = Category.objects.bulk_create(
        [
            Category(name="Category 1", slug="category-1"),
            Category(name="Category 2", slug="category-2"),
            Category(name="Category 3", slug="category-3"),
        ]
    )
    return categories


@pytest.fixture
def vehicle(category):
    vehicle = Entry.objects.create(
        name="Vehicle",
        slug="vehicle",
        type=EntryType.VEHICLE,
        document_number="123456789",
        category=category,
        is_published=True,
        email="vehicle@email.com",
    )
    return vehicle


@pytest.fixture
def vehicle_list(category):
    vehicles = Entry.objects.bulk_create(
        [
            Entry(
                name="Vehicle 1",
                slug="vehicle-1",
                type=EntryType.VEHICLE,
                document_number="123456789a",
                category=category,
                is_published=True,
                email="vehicle@email.com",
            ),
            Entry(
                name="Vehicle 2",
                slug="vehicle-2",
                type=EntryType.VEHICLE,
                document_number="123456789b",
                category=category,
                is_published=True,
                email="vehicle@email.com",
            ),
            Entry(
                name="Vehicle 3",
                slug="vehicle-3",
                type=EntryType.VEHICLE,
                document_number="123456789c",
                category=category,
                is_published=False,
                email="vehicle@email.com",
            ),
        ]
    )
    return vehicles


@pytest.fixture
def provider(category):
    provider = Entry.objects.create(
        name="Provider",
        slug="provider",
        type=EntryType.PROVIDER,
        document_number="123456789",
        category=category,
        is_published=True,
        email="provider@email.com",
    )
    return provider


@pytest.fixture
def provider_list(category):
    providers = Entry.objects.bulk_create(
        [
            Entry(
                name="Provider 1",
                slug="provider-1",
                type=EntryType.PROVIDER,
                document_number="123456789a",
                category=category,
                is_published=True,
                email="provider@email.com",
            ),
            Entry(
                name="Provider 2",
                slug="provider-2",
                type=EntryType.PROVIDER,
                document_number="123456789b",
                category=category,
                is_published=True,
                email="provider@email.com",
            ),
            Entry(
                name="Provider 3",
                slug="provider-3",
                type=EntryType.PROVIDER,
                document_number="123456789c",
                category=category,
                is_published=False,
                email="provider@email.com",
            ),
        ]
    )
    return providers


@pytest.fixture
def default_file():
    document_file = DocumentFile.objects.create(file="/path/to/file.pdf")
    return document_file


@pytest.fixture
def document_list(vehicle):
    default_files = DocumentFile.objects.bulk_create(
        [DocumentFile(file="/path/to/file.pdf"), DocumentFile(file="/path/to/file.pdf")]
    )
    documents = Document.objects.bulk_create(
        [
            Document(
                name="Document 1",
                entry=vehicle,
                default_file=default_files[0],
                is_published=True,
            ),
            Document(
                name="Document 2",
                entry=vehicle,
                default_file=default_files[1],
                is_published=False,
            ),
        ]
    )
    return documents


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


@pytest.fixture
def channel_city_1():
    channel = Channel.objects.create(
        name="Channel city 1",
        slug="c-city-1",
        is_active=True,
    )
    return channel


@pytest.fixture
def channel_city_2():
    channel = Channel.objects.create(
        name="Channel city 2",
        slug="c-city-2",
        is_active=True,
    )
    return channel
