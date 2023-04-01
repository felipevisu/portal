import graphene
import pytest
from django.utils.text import slugify

from portal.graphql.tests.utils import get_graphql_content

pytestmark = pytest.mark.django_db

UPDATE_ATTRIBUTE_VALUE_MUTATION = """
mutation AttributeValueUpdate($id: ID!, $input: AttributeValueUpdateInput!) {
    attributeValueUpdate(id: $id, input: $input) {
        errors {
            field
            message
            code
        }
        attributeValue {
            name
            slug
            value
        }
        attribute {
            choices(first: 10) {
                edges {
                    node {
                        name
                    }
                }
            }
        }
    }
}
"""


def test_update_attribute_value(
    staff_api_client,
    pink_attribute_value,
    permission_manage_attributes,
):
    # given
    query = UPDATE_ATTRIBUTE_VALUE_MUTATION
    value = pink_attribute_value
    node_id = graphene.Node.to_global_id("AttributeValue", value.id)
    name = "Crimson name"
    variables = {
        "id": node_id,
        "input": {"name": name},
    }

    # when
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_attributes]
    )

    # then
    content = get_graphql_content(response)
    data = content["data"]["attributeValueUpdate"]
    value.refresh_from_db()
    assert data["attributeValue"]["name"] == name == value.name
    assert data["attributeValue"]["slug"] == slugify(name)
    assert name in [
        value["node"]["name"] for value in data["attribute"]["choices"]["edges"]
    ]


def test_update_attribute_value_name_not_unique(
    staff_api_client,
    pink_attribute_value,
    permission_manage_attributes,
):
    # given
    query = UPDATE_ATTRIBUTE_VALUE_MUTATION
    value = pink_attribute_value.attribute.values.create(
        name="Example Name", slug="example-name", value="#RED"
    )
    node_id = graphene.Node.to_global_id("AttributeValue", value.id)
    variables = {"input": {"name": pink_attribute_value.name}, "id": node_id}

    # when
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_attributes]
    )

    # then
    content = get_graphql_content(response)
    data = content["data"]["attributeValueUpdate"]
    assert not data["errors"]
    assert data["attributeValue"]["slug"] == "pink-2"


def test_update_attribute_value_the_same_name_as_different_attribute_value(
    staff_api_client,
    size_attribute,
    color_attribute,
    permission_manage_attributes,
):
    """Ensure the attribute value with the same slug as value of different attribute
    can be set."""
    # given
    query = UPDATE_ATTRIBUTE_VALUE_MUTATION

    value = size_attribute.values.first()
    based_value = color_attribute.values.first()

    node_id = graphene.Node.to_global_id("AttributeValue", value.id)
    name = based_value.name
    variables = {"input": {"name": name}, "id": node_id}

    # when
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_attributes]
    )

    # then
    content = get_graphql_content(response)
    data = content["data"]["attributeValueUpdate"]
    value.refresh_from_db()
    assert data["attributeValue"]["name"] == name == value.name
    assert data["attributeValue"]["slug"] == based_value.slug
    assert name in [
        value["node"]["name"] for value in data["attribute"]["choices"]["edges"]
    ]
