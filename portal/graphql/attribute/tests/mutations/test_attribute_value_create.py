import graphene
import pytest
from django.core.exceptions import ValidationError
from django.utils.text import slugify

from portal.graphql.tests.utils import get_graphql_content

from .....attribute.models import AttributeValue
from ...mutations.validators import validate_value_is_unique

pytestmark = pytest.mark.django_db


def test_validate_value_is_unique(color_attribute):
    value = color_attribute.values.first()

    # a new value but with existing slug should raise an error
    with pytest.raises(ValidationError):
        validate_value_is_unique(color_attribute, AttributeValue(slug=value.slug))

    # a new value with a new slug should pass
    validate_value_is_unique(
        color_attribute, AttributeValue(slug="spanish-inquisition")
    )

    # value that already belongs to the attribute shouldn't be taken into account
    validate_value_is_unique(color_attribute, value)


CREATE_ATTRIBUTE_VALUE_MUTATION = """
    mutation createAttributeValue(
        $attributeId: ID!, $name: String!, $value: String
    ) {
    attributeValueCreate(
        attribute: $attributeId, input: { name: $name, value: $value }
    ) {
        errors {
            field
            message
            code
        }
        attribute {
            choices(first: 10) {
                edges {
                    node {
                        name
                        value
                    }
                }
            }
        }
        attributeValue {
            name
            slug
        }
    }
}
"""


def test_create_attribute_value(
    staff_api_client, color_attribute, permission_manage_attributes
):
    # given
    attribute = color_attribute
    query = CREATE_ATTRIBUTE_VALUE_MUTATION
    attribute_id = graphene.Node.to_global_id("Attribute", attribute.id)
    name = "test name"
    external_reference = "test-ext-ref"
    variables = {
        "name": name,
        "attributeId": attribute_id,
        "externalReference": external_reference,
    }

    # when
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_attributes]
    )

    # then
    content = get_graphql_content(response)
    data = content["data"]["attributeValueCreate"]
    assert not data["errors"]

    attr_data = data["attributeValue"]
    assert attr_data["name"] == name
    assert attr_data["slug"] == slugify(name)
    assert name in [
        value["node"]["name"] for value in data["attribute"]["choices"]["edges"]
    ]


def test_create_attribute_value_with_the_same_name_as_different_attribute_value(
    staff_api_client,
    attribute_without_values,
    color_attribute,
    permission_manage_attributes,
):
    """Ensure the attribute value with the same slug as value of different attribute
    can be created."""
    # given
    attribute = attribute_without_values
    query = CREATE_ATTRIBUTE_VALUE_MUTATION
    attribute_id = graphene.Node.to_global_id("Attribute", attribute.id)

    existing_value = color_attribute.values.first()

    name = existing_value.name
    variables = {"name": name, "attributeId": attribute_id}

    # when
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_attributes]
    )

    # then
    content = get_graphql_content(response)
    data = content["data"]["attributeValueCreate"]
    assert not data["errors"]

    attr_data = data["attributeValue"]
    assert attr_data["name"] == name
    assert attr_data["slug"] == existing_value.slug
    assert name in [
        value["node"]["name"] for value in data["attribute"]["choices"]["edges"]
    ]
