import graphene
import pytest

pytestmark = pytest.mark.django_db


ATTRIBUTE_VALUE_DELETE_MUTATION = """
    mutation AttributeValueDelete($id: ID!) {
        attributeValueDelete(id: $id) {
            attributeValue {
                name
                slug
            }
        }
    }
"""


def test_delete_attribute_value(
    staff_api_client,
    color_attribute,
    pink_attribute_value,
    permission_manage_attributes,
):
    # given
    value = color_attribute.values.get(name="Red")
    query = ATTRIBUTE_VALUE_DELETE_MUTATION
    node_id = graphene.Node.to_global_id("AttributeValue", value.id)
    variables = {"id": node_id}

    # when
    staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_attributes]
    )

    # then
    with pytest.raises(value._meta.model.DoesNotExist):
        value.refresh_from_db()
