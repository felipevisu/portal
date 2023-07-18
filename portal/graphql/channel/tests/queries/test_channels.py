import graphene
import pytest

from portal.entry.models import EntryChannelListing
from ....tests.utils import get_graphql_content, get_graphql_content_from_response

pytestmark = pytest.mark.django_db

QUERY_CHANNEL = """
    query getChannel($id: ID){
        channel(id: $id){
            id
            name
            slug
            totalEntries
        }
    }
"""


def test_query_channel(api_client, channel_city_1):
    # given
    channel_id = graphene.Node.to_global_id("Channel", channel_city_1.id)
    variables = {"id": channel_id}

    # when
    response = api_client.post_graphql(QUERY_CHANNEL, variables=variables)
    content = get_graphql_content(response)

    # then
    channel_data = content["data"]["channel"]
    assert channel_data["id"] == channel_id
    assert channel_data["name"] == channel_city_1.name
    assert channel_data["slug"] == channel_city_1.slug


def test_query_channel_by_invalid_id(api_client, channel_city_1):
    id = "bh/"
    variables = {"id": id}
    response = api_client.post_graphql(QUERY_CHANNEL, variables)
    content = get_graphql_content_from_response(response)
    assert len(content["errors"]) == 1
    assert content["errors"][0]["message"] == f"Couldn't resolve id: {id}."
    assert content["data"]["channel"] is None


def test_query_channel_with_entries_as_anonymous(
    api_client, channel_city_1, entries_channel_listings
):
    # given
    channel_id = graphene.Node.to_global_id("Channel", channel_city_1.id)
    variables = {"id": channel_id}

    # when
    response = api_client.post_graphql(QUERY_CHANNEL, variables=variables)
    content = get_graphql_content(response)

    # then
    channel_data = content["data"]["channel"]
    assert channel_data["totalEntries"] == 1


def test_query_channel_with_entries_as_staff(
    staff_api_client, channel_city_1, entries_channel_listings
):
    # given
    channel_id = graphene.Node.to_global_id("Channel", channel_city_1.id)
    variables = {"id": channel_id}

    # when
    response = staff_api_client.post_graphql(QUERY_CHANNEL, variables=variables)
    content = get_graphql_content(response)

    # then
    channel_data = content["data"]["channel"]
    assert channel_data["totalEntries"] == 2


QUERY_CHANNELS = """
    query {
        channels {
            name
            slug
            totalEntries
        }
    }
"""


def test_query_channels_as_staff_user(staff_api_client, channel_city_1, channel_city_2):
    # given

    # when
    response = staff_api_client.post_graphql(QUERY_CHANNELS, {})
    content = get_graphql_content(response)

    # then
    channels = content["data"]["channels"]
    assert len(channels) == 2
    assert {
        "slug": channel_city_1.slug,
        "name": channel_city_1.name,
        "totalEntries": 0,
    } in channels
    assert {
        "slug": channel_city_2.slug,
        "name": channel_city_2.name,
        "totalEntries": 0,
    } in channels


def test_query_channels_as_anonymous(api_client, channel_city_1, channel_city_2):
    # given
    channel_city_2.is_active = False
    channel_city_2.save()

    # when
    response = api_client.post_graphql(QUERY_CHANNELS, {})
    content = get_graphql_content(response)

    # then
    channels = content["data"]["channels"]
    assert len(channels) == 1
    assert {
        "slug": channel_city_1.slug,
        "name": channel_city_1.name,
        "totalEntries": 0,
    } in channels
    assert {
        "slug": channel_city_2.slug,
        "name": channel_city_2.name,
        "totalEntries": 0,
    } not in channels
