import pytest
from django.contrib.auth.models import Permission

from portal.account.models import User
from portal.attribute import AttributeInputType, AttributeType
from portal.attribute.models import Attribute, AttributeValue
from portal.attribute.utils import associate_attribute_values_to_instance
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
def permission_manage_channels():
    return Permission.objects.get(codename="manage_channels")


@pytest.fixture
def permission_manage_entries():
    return Permission.objects.get(codename="manage_entries")


@pytest.fixture
def permission_manage_plugins():
    return Permission.objects.get(codename="manage_plugins")


@pytest.fixture
def permission_manage_attributes():
    return Permission.objects.get(codename="manage_attributes")


@pytest.fixture
def staff_user():
    user = User.objects.create_user(  # type: ignore
        email="test@example.com",
        password="password",
        first_name="Leslie",
        last_name="Wade",
        is_staff=True,
        is_active=True,
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
def color_attribute():
    attribute = Attribute.objects.create(
        slug="color",
        name="Color",
        type=AttributeType.PROVIDER,
        input_type=AttributeInputType.MULTISELECT,
        filterable_in_website=True,
        filterable_in_dashboard=True,
    )
    AttributeValue.objects.create(attribute=attribute, name="Red", slug="red")
    AttributeValue.objects.create(attribute=attribute, name="Blue", slug="blue")
    return attribute


@pytest.fixture
def color_attribute_without_values():
    return Attribute.objects.create(
        slug="color",
        name="Color",
        type=AttributeType.PROVIDER,
        filterable_in_website=True,
        filterable_in_dashboard=True,
    )


@pytest.fixture
def attribute_without_values():
    return Attribute.objects.create(
        slug="dropdown",
        name="Dropdown",
        type=AttributeType.PROVIDER,
        filterable_in_website=True,
        filterable_in_dashboard=True,
        visible_in_website=True,
    )


@pytest.fixture
def pink_attribute_value(color_attribute):  # pylint: disable=W0613
    value = AttributeValue.objects.create(
        slug="pink", name="Pink", attribute=color_attribute, value="#FF69B4"
    )
    return value


@pytest.fixture
def size_attribute():
    attribute = Attribute.objects.create(
        slug="size",
        name="Size",
        type=AttributeType.DOCUMENT,
        filterable_in_website=True,
        filterable_in_dashboard=True,
    )
    AttributeValue.objects.create(attribute=attribute, name="Small", slug="small")
    AttributeValue.objects.create(attribute=attribute, name="Big", slug="big")
    return attribute


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


@pytest.fixture
def category():
    return Category.objects.create(
        name="Category", slug="category", type=EntryType.VEHICLE
    )


@pytest.fixture
def vehicle_category():
    return Category.objects.create(
        name="Category", slug="vehicle-category", type=EntryType.VEHICLE
    )


@pytest.fixture
def provider_category():
    return Category.objects.create(
        name="Category", slug="provider-category", type=EntryType.PROVIDER
    )


@pytest.fixture
def category_list():
    categories = Category.objects.bulk_create(
        [
            Category(name="Category 1", slug="category-1", type=EntryType.VEHICLE),
            Category(name="Category 2", slug="category-2", type=EntryType.VEHICLE),
            Category(name="Category 3", slug="category-3", type=EntryType.VEHICLE),
        ]
    )
    return categories


@pytest.fixture
def vehicle(vehicle_category):
    vehicle = Entry.objects.create(
        name="Vehicle",
        slug="vehicle",
        type=EntryType.VEHICLE,
        document_number="123456789",
        email="vehicle@email.com",
    )
    vehicle.categories.add(vehicle_category)
    return vehicle


@pytest.fixture
def vehicle_list(vehicle_category):
    vehicles = Entry.objects.bulk_create(
        [
            Entry(
                name="Vehicle 1",
                slug="vehicle-1",
                type=EntryType.VEHICLE,
                document_number="123456789a",
                email="vehicle@email.com",
            ),
            Entry(
                name="Vehicle 2",
                slug="vehicle-2",
                type=EntryType.VEHICLE,
                document_number="123456789b",
                email="vehicle@email.com",
            ),
            Entry(
                name="Vehicle 3",
                slug="vehicle-3",
                type=EntryType.VEHICLE,
                document_number="123456789c",
                email="vehicle@email.com",
            ),
        ]
    )
    for vehicle in vehicles:
        vehicle.categories.add(vehicle_category)
    return vehicles


@pytest.fixture
def provider(provider_category, color_attribute):
    provider = Entry.objects.create(
        name="Provider",
        slug="provider",
        type=EntryType.PROVIDER,
        document_number="123456789",
        email="provider@email.com",
    )
    provider.categories.add(provider_category)
    attribute_value = color_attribute.values.first()
    associate_attribute_values_to_instance(provider, color_attribute, attribute_value)
    return provider


@pytest.fixture
def provider_list(provider_category):
    providers = Entry.objects.bulk_create(
        [
            Entry(
                name="Provider 1",
                slug="provider-1",
                type=EntryType.PROVIDER,
                document_number="123456789a",
                email="provider@email.com",
            ),
            Entry(
                name="Provider 2",
                slug="provider-2",
                type=EntryType.PROVIDER,
                document_number="123456789b",
                email="provider@email.com",
            ),
            Entry(
                name="Provider 3",
                slug="provider-3",
                type=EntryType.PROVIDER,
                document_number="123456789c",
                email="provider@email.com",
            ),
        ]
    )
    for provider in providers:
        provider.categories.add(provider_category)
    return providers


@pytest.fixture
def document(vehicle):
    document = Document.objects.create(name="Document", entry=vehicle)
    default_file = DocumentFile.objects.create(
        file="/path/to/file.pdf", document=document
    )
    document.default_file = default_file
    document.save()
    return document


@pytest.fixture
def document_list(vehicle):
    documents = Document.objects.bulk_create(
        [
            Document(
                name="Document 1",
                entry=vehicle,
                is_published=True,
            ),
            Document(
                name="Document 2",
                entry=vehicle,
                is_published=False,
            ),
        ]
    )
    default_files = DocumentFile.objects.bulk_create(
        [
            DocumentFile(file="/path/to/file.pdf", document=documents[0]),
            DocumentFile(file="/path/to/file.pdf", document=documents[0]),
        ]
    )
    documents[0].default_file = default_files[0]
    documents[1].default_file = default_files[1]
    documents[0].save()
    documents[1].save()
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
