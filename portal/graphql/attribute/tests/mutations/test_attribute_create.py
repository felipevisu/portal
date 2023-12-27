import pytest
from django.utils.text import slugify

from portal.graphql.tests.utils import get_graphql_content

from ...enums import AttributeInputTypeEnum, AttributeTypeEnum

pytestmark = pytest.mark.django_db


CREATE_ATTRIBUTE_MUTATION = """
    mutation createAttribute(
        $input: AttributeCreateInput!
    ){
        attributeCreate(input: $input) {
            errors {
                field
                message
                code
            }
            attribute {
                name
                slug
                type
                inputType
                filterableInWebsite
                filterableInDashboard
                choices(first: 10) {
                    edges {
                        node {
                            name
                            slug
                            value
                            file {
                                url
                            }
                        }
                    }
                }
            }
        }
    }
"""


def test_create_attribute_and_attribute_values(
    staff_api_client, permission_manage_attributes
):
    # given
    attribute_name = "Example name"
    name = "Value name"
    variables = {
        "input": {
            "name": attribute_name,
            "values": [{"name": name}],
            "type": AttributeTypeEnum.ENTRY_TYPE.name,
        }
    }

    # when
    response = staff_api_client.post_graphql(
        CREATE_ATTRIBUTE_MUTATION,
        variables,
        permissions=[permission_manage_attributes],
    )

    # then
    content = get_graphql_content(response)
    assert not content["data"]["attributeCreate"]["errors"]
    data = content["data"]["attributeCreate"]

    # Check if the attribute was correctly created
    assert data["attribute"]["name"] == attribute_name
    assert data["attribute"]["slug"] == slugify(
        attribute_name
    ), "The default slug should be the slugified name"

    # Check if the attribute values were correctly created
    assert len(data["attribute"]["choices"]) == 1
    assert data["attribute"]["type"] == AttributeTypeEnum.ENTRY_TYPE.name
    assert data["attribute"]["choices"]["edges"][0]["node"]["name"] == name
    assert data["attribute"]["choices"]["edges"][0]["node"]["slug"] == slugify(name)


def test_create_attribute_with_plain_text_input_type(
    staff_api_client, permission_manage_attributes
):
    # given
    query = CREATE_ATTRIBUTE_MUTATION

    attribute_name = "Example name"
    variables = {
        "input": {
            "name": attribute_name,
            "type": AttributeTypeEnum.ENTRY_TYPE.name,
            "inputType": AttributeInputTypeEnum.PLAIN_TEXT.name,
        }
    }

    # when
    response = staff_api_client.post_graphql(
        query,
        variables,
        permissions=[permission_manage_attributes],
    )

    # then
    content = get_graphql_content(response)
    assert not content["data"]["attributeCreate"]["errors"]
    data = content["data"]["attributeCreate"]

    # Check if the attribute was correctly created
    assert data["attribute"]["name"] == attribute_name
    assert data["attribute"]["slug"] == slugify(
        attribute_name
    ), "The default slug should be the slugified name"

    # Check if the attribute values were correctly created
    assert len(data["attribute"]["choices"]["edges"]) == 0
    assert data["attribute"]["type"] == AttributeTypeEnum.ENTRY_TYPE.name
    assert data["attribute"]["inputType"] == AttributeInputTypeEnum.PLAIN_TEXT.name
