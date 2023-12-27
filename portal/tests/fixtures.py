import pytest
from django.contrib.auth.models import Permission

from portal.account.models import User
from portal.attribute import AttributeInputType, AttributeType
from portal.attribute.models import Attribute, AttributeValue
from portal.attribute.utils import associate_attribute_values_to_instance
from portal.channel.models import Channel
from portal.document.models import Document, DocumentFile
from portal.entry import EntryType as EntryTypeEnum
from portal.entry.models import Category, Entry, EntryChannelListing, EntryType
from portal.investment.models import Investment, Item


@pytest.fixture
def permission_manage_investments():
    return Permission.objects.get(codename="manage_investments")


@pytest.fixture
def permission_manage_entry_types():
    return Permission.objects.get(codename="manage_entry_types")


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
def entry_type():
    entry_type = EntryType.objects.create(name="Entry Type", slug="entry-type")
    return entry_type


@pytest.fixture
def vehicle_entry_type():
    entry_type = EntryType.objects.create(name="Vehicle", slug="vehicle")
    return entry_type


@pytest.fixture
def provider_entry_type():
    entry_type = EntryType.objects.create(name="Provider", slug="provider")
    return entry_type


@pytest.fixture
def entry_type_list():
    entry_types = EntryType.objects.bulk_create(
        [
            EntryType(name="Entry Type 1", slug="entry-type-1"),
            EntryType(name="Entry Type 2", slug="entry-type-2"),
        ]
    )
    return entry_types


@pytest.fixture
def color_attribute(vehicle_entry_type, provider_entry_type):
    attribute = Attribute.objects.create(
        slug="color",
        name="Color",
        type=AttributeType.ENTRY_TYPE,
        input_type=AttributeInputType.MULTISELECT,
        filterable_in_website=True,
        filterable_in_dashboard=True,
    )
    attribute.entry_types.add(*[vehicle_entry_type, provider_entry_type])
    AttributeValue.objects.create(attribute=attribute, name="Red", slug="red")
    AttributeValue.objects.create(attribute=attribute, name="Blue", slug="blue")
    return attribute


@pytest.fixture
def color_attribute_without_values():
    return Attribute.objects.create(
        slug="color",
        name="Color",
        type=AttributeType.ENTRY_TYPE,
        filterable_in_website=True,
        filterable_in_dashboard=True,
    )


@pytest.fixture
def attribute_without_values():
    return Attribute.objects.create(
        slug="dropdown",
        name="Dropdown",
        type=AttributeType.ENTRY_TYPE,
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
def size_attribute(vehicle_entry_type, provider_entry_type):
    attribute = Attribute.objects.create(
        slug="size",
        name="Size",
        type=AttributeType.ENTRY_TYPE,
        filterable_in_website=True,
        filterable_in_dashboard=True,
    )
    attribute.entry_types.add(*[vehicle_entry_type, provider_entry_type])
    AttributeValue.objects.create(attribute=attribute, name="Small", slug="small")
    AttributeValue.objects.create(attribute=attribute, name="Big", slug="big")
    return attribute


@pytest.fixture
def attribute_generator():
    def create_attribute(
        external_reference="attributeExtRef",
        slug="attr",
        name="Attr",
        type=AttributeType.ENTRY_TYPE,
        filterable_in_website=True,
        filterable_in_dashboard=True,
        available_in_grid=True,
    ):
        attribute, _ = Attribute.objects.get_or_create(
            external_reference=external_reference,
            slug=slug,
            name=name,
            type=type,
            filterable_in_website=filterable_in_website,
            filterable_in_dashboard=filterable_in_dashboard,
        )

        return attribute

    return create_attribute


@pytest.fixture
def attribute_value_generator(attribute_generator):
    def create_attribute_value(
        attribute=None,
        name="Attr Value",
        slug="attr-value",
        value="",
    ):
        if attribute is None:
            attribute = attribute_generator()
        attribute_value, _ = AttributeValue.objects.get_or_create(
            attribute=attribute,
            name=name,
            slug=slug,
            value=value,
        )

        return attribute_value

    return create_attribute_value


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
        name="Category", slug="category", type=EntryTypeEnum.VEHICLE
    )


@pytest.fixture
def vehicle_category():
    return Category.objects.create(
        name="Category", slug="vehicle-category", type=EntryTypeEnum.VEHICLE
    )


@pytest.fixture
def provider_category():
    return Category.objects.create(
        name="Category", slug="provider-category", type=EntryTypeEnum.PROVIDER
    )


@pytest.fixture
def category_list():
    categories = Category.objects.bulk_create(
        [
            Category(name="Category 1", slug="category-1", type=EntryTypeEnum.VEHICLE),
            Category(name="Category 2", slug="category-2", type=EntryTypeEnum.VEHICLE),
            Category(name="Category 3", slug="category-3", type=EntryTypeEnum.VEHICLE),
        ]
    )
    return categories


@pytest.fixture
def vehicle(vehicle_category, vehicle_entry_type):
    vehicle = Entry.objects.create(
        name="Vehicle",
        slug="vehicle",
        type=EntryTypeEnum.VEHICLE,
        document_number="123456789",
        email="vehicle@email.com",
        entry_type=vehicle_entry_type,
    )
    vehicle.categories.add(vehicle_category)
    return vehicle


@pytest.fixture
def vehicle_list(vehicle_category, vehicle_entry_type):
    vehicles = Entry.objects.bulk_create(
        [
            Entry(
                name="Vehicle 1",
                slug="vehicle-1",
                type=EntryTypeEnum.VEHICLE,
                document_number="123456789a",
                email="vehicle@email.com",
                entry_type=vehicle_entry_type,
            ),
            Entry(
                name="Vehicle 2",
                slug="vehicle-2",
                type=EntryTypeEnum.VEHICLE,
                document_number="123456789b",
                email="vehicle@email.com",
                entry_type=vehicle_entry_type,
            ),
            Entry(
                name="Vehicle 3",
                slug="vehicle-3",
                type=EntryTypeEnum.VEHICLE,
                document_number="123456789c",
                email="vehicle@email.com",
                entry_type=vehicle_entry_type,
            ),
        ]
    )
    for vehicle in vehicles:
        vehicle.categories.add(vehicle_category)
    return vehicles


@pytest.fixture
def entries_channel_listings(vehicle, provider, channel_city_1):
    listings = EntryChannelListing.objects.bulk_create(
        [
            EntryChannelListing(
                entry=vehicle,
                channel=channel_city_1,
                is_published=False,
                is_active=False,
            ),
            EntryChannelListing(
                entry=provider,
                channel=channel_city_1,
                is_published=True,
                is_active=True,
            ),
        ]
    )
    return listings


@pytest.fixture
def provider(provider_category, provider_entry_type, color_attribute):
    provider = Entry.objects.create(
        name="Provider",
        slug="provider",
        type=EntryTypeEnum.PROVIDER,
        document_number="123456789",
        email="provider@email.com",
        entry_type=provider_entry_type,
    )
    provider.categories.add(provider_category)
    attribute_value = color_attribute.values.first()
    associate_attribute_values_to_instance(provider, color_attribute, attribute_value)
    return provider


@pytest.fixture
def provider_list(provider_category, provider_entry_type):
    providers = Entry.objects.bulk_create(
        [
            Entry(
                name="Provider 1",
                slug="provider-1",
                type=EntryTypeEnum.PROVIDER,
                document_number="123456789a",
                email="provider@email.com",
                entry_type=provider_entry_type,
            ),
            Entry(
                name="Provider 2",
                slug="provider-2",
                type=EntryTypeEnum.PROVIDER,
                document_number="123456789b",
                email="provider@email.com",
                entry_type=provider_entry_type,
            ),
            Entry(
                name="Provider 3",
                slug="provider-3",
                type=EntryTypeEnum.PROVIDER,
                document_number="123456789c",
                email="provider@email.com",
                entry_type=provider_entry_type,
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
def investment(channel_city_1):
    return Investment.objects.create(
        year=2022, month=3, is_published=False, channel=channel_city_1
    )


@pytest.fixture
def published_investment(channel_city_1):
    return Investment.objects.create(
        year=2022, month=2, is_published=True, channel=channel_city_1
    )


@pytest.fixture
def investment_with_items():
    investment = Investment.objects.create(year=2022, month=1)
    Item.objects.create(name="TV", slug="tv", value=100, investment=investment),
    Item.objects.create(name="Radio", slug="radio", value=100, investment=investment),
    Item.objects.create(
        name="Internet", slug="internet", value=200, investment=investment
    )
    return investment
