import graphene
import pytest

from portal.entry import EntryType
from portal.entry.models import Category

from ....tests.utils import get_graphql_content

pytestmark = pytest.mark.django_db


CREATE_CATEGORY_MUTATION = """
    mutation CategoryCreate($input: CategoryInput!){
        categoryCreate(input: $input){
            category{
                id
                name
                slug
                type
            }
            errors{
                message
                field
                code
            }
        }
    }
"""


def test_category_create(staff_api_client, permission_manage_categories):
    input = {"name": "Category", "slug": "category", "type": "VEHICLE"}
    variables = {"input": input}
    response = staff_api_client.post_graphql(
        CREATE_CATEGORY_MUTATION,
        variables=variables,
        permissions=[permission_manage_categories],
    )
    content = get_graphql_content(response)
    data = content["data"]["categoryCreate"]
    assert not data["errors"]
    assert data["category"]["name"] == input["name"]
    assert data["category"]["slug"] == input["slug"]


def test_category_create_without_slug(staff_api_client, permission_manage_categories):
    input = {"name": "Category", "type": "VEHICLE"}
    variables = {"input": input}
    response = staff_api_client.post_graphql(
        CREATE_CATEGORY_MUTATION,
        variables=variables,
        permissions=[permission_manage_categories],
    )
    content = get_graphql_content(response)
    data = content["data"]["categoryCreate"]
    assert not data["errors"]
    assert data["category"]["name"] == input["name"]
    assert data["category"]["slug"] == "category"


def test_category_create_with_existent_name(
    staff_api_client, category, permission_manage_categories
):
    input = {"name": "Category", "type": "VEHICLE"}
    variables = {"input": input}
    response = staff_api_client.post_graphql(
        CREATE_CATEGORY_MUTATION,
        variables=variables,
        permissions=[permission_manage_categories],
    )
    content = get_graphql_content(response)
    data = content["data"]["categoryCreate"]
    assert not data["errors"]
    assert data["category"]["name"] == input["name"]
    assert data["category"]["slug"] == "category-2"


def test_category_create_without_name(staff_api_client, permission_manage_categories):
    input = {"type": "VEHICLE"}
    variables = {"input": input}
    response = staff_api_client.post_graphql(
        CREATE_CATEGORY_MUTATION,
        variables=variables,
        permissions=[permission_manage_categories],
    )
    content = get_graphql_content(response)
    data = content["data"]["categoryCreate"]
    assert not data["errors"] == []
    assert data["errors"][0]["field"] == "name"


def test_category_create_without_type(staff_api_client, permission_manage_categories):
    input = {"name": "Category"}
    variables = {"input": input}
    response = staff_api_client.post_graphql(
        CREATE_CATEGORY_MUTATION,
        variables=variables,
        permissions=[permission_manage_categories],
    )
    content = get_graphql_content(response)
    data = content["data"]["categoryCreate"]
    assert not data["errors"] == []
    assert data["errors"][0]["field"] == "type"


UPDATE_CATEGORY_MUTATION = """
    mutation CategoryUpdate($id: ID!, $input: CategoryInput!){
        categoryUpdate(id: $id, input: $input){
            category{
                id
                name
                slug
                type
            }
            errors{
                message
                field
                code
            }
        }
    }
"""


def test_category_update(staff_api_client, category, permission_manage_categories):
    input = {"name": "Category Updated"}
    category_id = graphene.Node.to_global_id("Category", category.pk)
    variables = {"id": category_id, "input": input}
    response = staff_api_client.post_graphql(
        UPDATE_CATEGORY_MUTATION,
        variables=variables,
        permissions=[permission_manage_categories],
    )
    category.refresh_from_db()
    content = get_graphql_content(response)
    data = content["data"]["categoryUpdate"]
    assert not data["errors"]
    assert category.name == input["name"]


def test_category_update_with_existent_slug(
    staff_api_client, category, permission_manage_categories
):
    new_category = Category.objects.create(
        name="New Category", slug="new-category", type=EntryType.VEHICLE
    )
    input = {"slug": "category"}
    category_id = graphene.Node.to_global_id("Category", new_category.pk)
    variables = {"id": category_id, "input": input}
    response = staff_api_client.post_graphql(
        UPDATE_CATEGORY_MUTATION,
        variables=variables,
        permissions=[permission_manage_categories],
    )
    category.refresh_from_db()
    content = get_graphql_content(response)
    data = content["data"]["categoryUpdate"]
    assert data["errors"]
    assert data["errors"][0]["field"] == "slug"


CATEGORY_DELETE_MUTATION = """
    mutation($id: ID!) {
        categoryDelete(id: $id) {
            category {
                id
            }
            errors {
                field
                message
            }
        }
    }
"""


def test_category_delete(
    staff_api_client,
    permission_manage_categories,
    category,
):
    category_id = graphene.Node.to_global_id("Category", category.id)
    variables = {"id": category_id}
    response = staff_api_client.post_graphql(
        CATEGORY_DELETE_MUTATION,
        variables=variables,
        permissions=[permission_manage_categories],
    )
    content = get_graphql_content(response)
    data = content["data"]["categoryDelete"]

    assert data["errors"] == []
    assert data["category"]["id"] == category_id


def test_category_delete_with_invalid_id(
    staff_api_client,
    permission_manage_categories,
    category,
):
    variables = {"id": "'"}
    response = staff_api_client.post_graphql(
        CATEGORY_DELETE_MUTATION,
        variables=variables,
        permissions=[permission_manage_categories],
    )
    content = get_graphql_content(response)
    data = content["data"]["categoryDelete"]

    assert data["category"] is None
    assert data["errors"] is not None
    assert data["errors"][0]["field"] == "id"
