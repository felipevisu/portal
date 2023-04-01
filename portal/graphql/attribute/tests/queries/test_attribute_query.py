import graphene
import pytest
from graphene.utils.str_converters import to_camel_case

from portal.attribute import AttributeInputType, AttributeType
from portal.attribute.models import Attribute
from portal.graphql.tests.utils import (
    get_graphql_content,
    get_graphql_content_from_response,
)

pytestmark = pytest.mark.django_db


def test_get_single_attribute_by_id_as_customer(
    api_client, color_attribute_without_values
):
    attribute_gql_id = graphene.Node.to_global_id(
        "Attribute", color_attribute_without_values.id
    )
    query = """
    query($id: ID!) {
        attribute(id: $id) {
            id
            name
            slug
        }
    }
    """
    content = get_graphql_content(
        api_client.post_graphql(query, {"id": attribute_gql_id})
    )

    assert content["data"]["attribute"], "Should have found an attribute"
    assert content["data"]["attribute"]["id"] == attribute_gql_id
    assert content["data"]["attribute"]["slug"] == color_attribute_without_values.slug


def test_get_single_attribute_by_slug_as_customer(
    api_client, color_attribute_without_values
):
    attribute_gql_slug = color_attribute_without_values.slug
    query = """
    query($slug: String!) {
        attribute(slug: $slug) {
            id
            name
            slug
        }
    }
    """
    content = get_graphql_content(
        api_client.post_graphql(query, {"slug": attribute_gql_slug})
    )

    assert content["data"]["attribute"], "Should have found an attribute"
    assert content["data"]["attribute"]["slug"] == attribute_gql_slug
    assert content["data"]["attribute"]["id"] == graphene.Node.to_global_id(
        "Attribute", color_attribute_without_values.id
    )


QUERY_ATTRIBUTE = """
    query($id: ID!, $query: String) {
        attribute(id: $id) {
            id
            slug
            name
            inputType
            type
            choices(first: 10, filter: {search: $query}) {
                edges {
                    node {
                        slug
                        inputType
                        value
                    }
                }
            }
            valueRequired
            visibleInWebsite
            filterableInWebsite
            filterableInDashboard
        }
    }
"""


def test_get_single_entry_attribute_by_staff(
    staff_api_client, color_attribute_without_values, permission_manage_attributes
):
    staff_api_client.user.user_permissions.add(permission_manage_attributes)
    attribute_gql_id = graphene.Node.to_global_id(
        "Attribute", color_attribute_without_values.id
    )
    query = QUERY_ATTRIBUTE
    content = get_graphql_content(
        staff_api_client.post_graphql(query, {"id": attribute_gql_id})
    )

    assert content["data"]["attribute"], "Should have found an attribute"
    assert content["data"]["attribute"]["id"] == attribute_gql_id
    assert content["data"]["attribute"]["slug"] == color_attribute_without_values.slug
    assert (
        content["data"]["attribute"]["valueRequired"]
        == color_attribute_without_values.value_required
    )
    assert (
        content["data"]["attribute"]["visibleInWebsite"]
        == color_attribute_without_values.visible_in_website
    )
    assert (
        content["data"]["attribute"]["filterableInWebsite"]
        == color_attribute_without_values.filterable_in_website
    )
    assert (
        content["data"]["attribute"]["filterableInDashboard"]
        == color_attribute_without_values.filterable_in_dashboard
    )


def test_get_single_entry_attribute_by_app(
    staff_api_client, color_attribute_without_values, permission_manage_attributes
):
    staff_api_client.user.user_permissions.add(permission_manage_attributes)
    attribute_gql_id = graphene.Node.to_global_id(
        "Attribute", color_attribute_without_values.id
    )
    query = QUERY_ATTRIBUTE
    content = get_graphql_content(
        staff_api_client.post_graphql(query, {"id": attribute_gql_id})
    )

    assert content["data"]["attribute"], "Should have found an attribute"
    assert content["data"]["attribute"]["id"] == attribute_gql_id
    assert content["data"]["attribute"]["slug"] == color_attribute_without_values.slug
    assert (
        content["data"]["attribute"]["valueRequired"]
        == color_attribute_without_values.value_required
    )
    assert (
        content["data"]["attribute"]["visibleInWebsite"]
        == color_attribute_without_values.visible_in_website
    )
    assert (
        content["data"]["attribute"]["filterableInWebsite"]
        == color_attribute_without_values.filterable_in_website
    )
    assert (
        content["data"]["attribute"]["filterableInDashboard"]
        == color_attribute_without_values.filterable_in_dashboard
    )


def test_query_attribute_by_invalid_id(
    staff_api_client, color_attribute_without_values
):
    id = "bh/"
    variables = {"id": id}
    response = staff_api_client.post_graphql(QUERY_ATTRIBUTE, variables)
    content = get_graphql_content_from_response(response)
    assert len(content["errors"]) == 1
    assert content["errors"][0]["message"] == f"Couldn't resolve id: {id}."
    assert content["data"]["attribute"] is None


@pytest.mark.parametrize(
    "attribute, expected_value",
    (
        ("filterable_in_website", True),
        ("filterable_in_dashboard", True),
        ("visible_in_website", True),
        ("value_required", False),
    ),
)
def test_retrieving_the_restricted_attributes_restricted(
    staff_api_client,
    color_attribute,
    permission_manage_attributes,
    attribute,
    expected_value,
):
    """Checks if the attributes are restricted and if their default value
    is the expected one."""

    attribute = to_camel_case(attribute)
    query = (
        """
        {
          attributes(first: 10) {
            edges {
              node {
                %s
              }
            }
          }
        }
    """
        % attribute
    )

    found_attributes = get_graphql_content(
        staff_api_client.post_graphql(query, permissions=[permission_manage_attributes])
    )["data"]["attributes"]["edges"]

    assert len(found_attributes) == 1
    assert found_attributes[0]["node"][attribute] == expected_value


@pytest.mark.parametrize(
    "input_type, expected_with_choice_return",
    [
        (AttributeInputType.DROPDOWN, True),
        (AttributeInputType.MULTISELECT, True),
        (AttributeInputType.FILE, False),
        (AttributeInputType.NUMERIC, False),
        (AttributeInputType.BOOLEAN, False),
    ],
)
def test_attributes_with_choice_flag(
    api_client,
    input_type,
    expected_with_choice_return,
):
    attribute = Attribute.objects.create(
        slug=input_type,
        name=input_type.upper(),
        type=AttributeType.PROVIDER,
        input_type=input_type,
        filterable_in_website=True,
        filterable_in_dashboard=True,
    )

    attribute_gql_id = graphene.Node.to_global_id("Attribute", attribute.id)
    query = """
    query($id: ID!) {
        attribute(id: $id) {
            id
            inputType
            withChoices

        }
    }
    """
    content = get_graphql_content(
        api_client.post_graphql(query, {"id": attribute_gql_id})
    )
    assert content["data"]["attribute"]["id"] == attribute_gql_id
    assert content["data"]["attribute"]["inputType"] == input_type.upper().replace(
        "-", "_"
    )
    assert content["data"]["attribute"]["withChoices"] == expected_with_choice_return
