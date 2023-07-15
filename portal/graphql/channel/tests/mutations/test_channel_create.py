import graphene
import pytest
from django.utils.text import slugify
from portal.graphql.tests.utils import assert_no_permission, get_graphql_content
from portal.channel.models import Channel

pytestmark = pytest.mark.django_db

CHANNEL_CREATE_MUTATION = """
    mutation CreateChannel($input: ChannelInput!){
        channelCreate(input: $input){
            channel{
                id
                name
                slug
                isActive
            }
            errors{
                field
                code
                message
            }
        }
    }
"""


def test_channel_create_mutation_as_staff_user(
    permission_manage_channels,
    staff_api_client,
):
    # given
    name = "testName"
    slug = "test_slug"
    variables = {"input": {"name": name, "slug": slug}}

    # when
    response = staff_api_client.post_graphql(
        CHANNEL_CREATE_MUTATION,
        variables=variables,
        permissions=(permission_manage_channels,),
    )
    content = get_graphql_content(response)

    # then
    data = content["data"]["channelCreate"]
    assert not data["errors"]
    channel_data = data["channel"]
    channel = Channel.objects.get()
    assert channel_data["name"] == channel.name == name
    assert channel_data["slug"] == channel.slug == slug


def test_channel_create_mutation_as_customer(api_client):
    # given
    name = "testName"
    slug = "test_slug"
    variables = {"input": {"name": name, "slug": slug}}

    # when
    response = api_client.post_graphql(
        CHANNEL_CREATE_MUTATION,
        variables=variables,
        permissions=(),
    )

    # then
    assert_no_permission(response)


def test_channel_create_mutation_slugify_slug_field(
    permission_manage_channels,
    staff_api_client,
):
    # given
    name = "testName"
    slug = "Invalid slug"
    variables = {
        "input": {
            "name": name,
            "slug": slug,
        }
    }

    # when
    response = staff_api_client.post_graphql(
        CHANNEL_CREATE_MUTATION,
        variables=variables,
        permissions=(permission_manage_channels,),
    )
    content = get_graphql_content(response)

    # then
    channel_data = content["data"]["channelCreate"]["channel"]
    assert channel_data["slug"] == slugify(slug)


def test_channel_create_mutation_with_duplicated_slug(
    permission_manage_channels, staff_api_client, channel_city_1
):
    # given
    name = "New Channel"
    slug = channel_city_1.slug
    variables = {"input": {"name": name, "slug": slug}}

    # when
    response = staff_api_client.post_graphql(
        CHANNEL_CREATE_MUTATION,
        variables=variables,
        permissions=(permission_manage_channels,),
    )
    content = get_graphql_content(response)

    # then
    error = content["data"]["channelCreate"]["errors"][0]
    assert error["field"] == "slug"
