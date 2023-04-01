import graphene
import pytest

from portal.graphql.tests.utils import get_graphql_content

pytestmark = pytest.mark.django_db

ATTRIBUTE_DELETE_MUTATION = """
    mutation deleteAttribute($id: ID!) {
        attributeDelete(id: $id) {
            errors {
                field
                message
            }
            attribute {
                id
            }
        }
    }
"""


def test_delete_attribute(
    staff_api_client, color_attribute, permission_manage_attributes
):
    # given
    attribute = color_attribute
    query = ATTRIBUTE_DELETE_MUTATION
    node_id = graphene.Node.to_global_id("Attribute", attribute.id)
    variables = {"id": node_id}

    # when
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_attributes]
    )

    # then
    content = get_graphql_content(response)
    data = content["data"]["attributeDelete"]
    assert data["attribute"]["id"] == variables["id"]
    with pytest.raises(attribute._meta.model.DoesNotExist):
        attribute.refresh_from_db()
