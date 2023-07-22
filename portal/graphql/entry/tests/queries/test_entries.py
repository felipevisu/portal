import json

import graphene
import pytest

from portal.core.exceptions import PermissionDenied
from portal.entry.models import EntryChannelListing

from ....tests.utils import get_graphql_content, get_graphql_content_from_response

pytestmark = pytest.mark.django_db

QUERY_ENTRY = """
    query ($id: ID, $slug: String, $channel: String){
        entry(
            id: $id,
            slug: $slug,
            channel: $channel
        ) {
            id
            name
            slug
            documentNumber
            email
        }
    }
"""


def test_entry_query_by_id_as_anonymous_without_channel(api_client, vehicle):
    variables = {"id": graphene.Node.to_global_id("Entry", vehicle.pk)}
    response = api_client.post_graphql(QUERY_ENTRY, variables=variables)
    content = get_graphql_content(response)
    entry_data = content["data"]["entry"]
    assert entry_data is None


def test_entry_query_by_id_as_staff_without_channel(staff_api_client, vehicle):
    variables = {"id": graphene.Node.to_global_id("Entry", vehicle.pk)}
    response = staff_api_client.post_graphql(QUERY_ENTRY, variables=variables)
    content = get_graphql_content(response)
    entry_data = content["data"]["entry"]
    assert entry_data is not None
    assert entry_data["name"] == vehicle.name


def test_entry_query_by_id_as_anonymous_with_channel(
    api_client, vehicle, channel_city_1
):
    EntryChannelListing.objects.create(
        entry=vehicle, channel=channel_city_1, is_published=True, is_active=True
    )
    variables = {
        "id": graphene.Node.to_global_id("Entry", vehicle.pk),
        "channel": channel_city_1.slug,
    }
    response = api_client.post_graphql(QUERY_ENTRY, variables=variables)
    content = get_graphql_content(response)
    entry_data = content["data"]["entry"]
    assert entry_data is not None
    assert entry_data["name"] == vehicle.name


def test_entry_query_by_id_as_anonymous_with_channel_unpublished(
    api_client, vehicle, channel_city_2
):
    variables = {
        "id": graphene.Node.to_global_id("Entry", vehicle.pk),
        "channel": channel_city_2.slug,
    }
    response = api_client.post_graphql(QUERY_ENTRY, variables=variables)
    content = get_graphql_content(response)
    entry_data = content["data"]["entry"]
    assert entry_data is None


QUERY_ENTRY_CHANNEL_LISTINGS = """
    query ($id: ID, $slug: String, $channel: String){
        entry(
            id: $id,
            slug: $slug,
            channel: $channel
        ) {
            id
            name
            slug
            email
            documentNumber
            channelListings{
                id
                isPublished
                isActive
                channel{
                    id
                    name
                }
            }
        }
    }
"""


def test_entry_channel_listings_query_by_id_as_anonymous(
    api_client, vehicle, channel_city_1
):
    EntryChannelListing.objects.create(
        entry=vehicle, channel=channel_city_1, is_published=True, is_active=True
    )
    variables = {
        "id": graphene.Node.to_global_id("Entry", vehicle.pk),
        "channel": channel_city_1.slug,
    }
    response = api_client.post_graphql(
        QUERY_ENTRY_CHANNEL_LISTINGS, variables=variables
    )
    with pytest.raises(Exception) as e:
        get_graphql_content(response)


def test_entry_channel_listings_query_by_id_as_staff(
    staff_api_client, vehicle, channel_city_1, permission_manage_entries
):
    EntryChannelListing.objects.create(
        entry=vehicle, channel=channel_city_1, is_published=True, is_active=True
    )
    variables = {
        "id": graphene.Node.to_global_id("Entry", vehicle.pk),
        "channel": channel_city_1.slug,
    }
    response = staff_api_client.post_graphql(
        QUERY_ENTRY_CHANNEL_LISTINGS,
        variables=variables,
        permissions=[permission_manage_entries],
    )
    content = get_graphql_content(response)
    data = content["data"]["entry"]
    assert data is not None
    assert len(data["channelListings"]) == 1


QUERY_ENTRY_ATTRIBUTES = """
    query ($id: ID, $slug: String, $channel: String){
        entry(
            id: $id,
            slug: $slug,
            channel: $channel
        ) {
            id
            name
            slug
            email
            documentNumber
            attributes {
                attribute {
                    name
                }
                values {
                    name
                }
            }
        }
    }
"""


def test_entry_with_attributes_query_by_id_as_staff(
    staff_api_client, provider, channel_city_1
):
    EntryChannelListing.objects.create(
        entry=provider, channel=channel_city_1, is_published=True, is_active=True
    )
    variables = {
        "id": graphene.Node.to_global_id("Entry", provider.pk),
        "channel": channel_city_1.slug,
    }
    response = staff_api_client.post_graphql(
        QUERY_ENTRY_ATTRIBUTES, variables=variables
    )
    content = get_graphql_content(response)
    data = content["data"]["entry"]
    assert len(data["attributes"]) == 1


def test_entry_with_attributes_query_by_id_as_anonymous(
    api_client, provider, channel_city_1, color_attribute
):
    EntryChannelListing.objects.create(
        entry=provider, channel=channel_city_1, is_published=True, is_active=True
    )
    color_attribute.visible_in_website = False
    color_attribute.save()
    variables = {
        "id": graphene.Node.to_global_id("Entry", provider.pk),
        "channel": channel_city_1.slug,
    }
    response = api_client.post_graphql(QUERY_ENTRY_ATTRIBUTES, variables=variables)
    content = get_graphql_content(response)
    data = content["data"]["entry"]
    assert len(data["attributes"]) == 0
