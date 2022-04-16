import graphene
import pytest

from ...tests.utils import get_graphql_content

pytestmark = pytest.mark.django_db

QUERY_CATEGORY = """
    query Category($id: ID, $slug: String) {
        category(id: $id, slug: $slug) {
            id
            name
            slug
        }
    }
"""

QUERY_CATEGORIES = """
    query Categories{
        categories{
            edges{
                node{
                    id
                    name
                    slug
                }
            }
        }
    }
"""


def test_category_query_by_id(api_client, category):
    category_id = graphene.Node.to_global_id("Category", category.pk)
    variables = {"id": category_id}
    response = api_client.post_graphql(QUERY_CATEGORY, variables=variables)
    content = get_graphql_content(response)
    data = content['data']['category']

    assert data['id'] == category_id
    assert data['name'] == category.name
    assert data['slug'] == category.slug


def test_category_query_by_slug(api_client, category):
    variables = {"slug": category.slug}
    response = api_client.post_graphql(QUERY_CATEGORY, variables=variables)
    content = get_graphql_content(response)
    data = content['data']['category']

    assert data['name'] == category.name
    assert data['slug'] == category.slug


def test_category_query_by_invalid_id(api_client):
    category_id = "'"
    variables = {"id": category_id}
    response = api_client.post_graphql(QUERY_CATEGORY, variables=variables)
    content = get_graphql_content(response, ignore_errors=True)
    assert len(content["errors"]) == 1
    assert content["errors"][0]["message"] == f"Couldn't resolve id: {category_id}."
    assert content["data"]["category"] is None


def test_categories_query(api_client, category):
    response = api_client.post_graphql(QUERY_CATEGORIES)
    content = get_graphql_content(response, ignore_errors=True)
    data = content['data']['categories']
    global_id = graphene.Node.to_global_id("Category", category.pk)

    assert len(data['edges']) == 1
    assert data['edges'][0]['node']['id'] == global_id


def test_categories_query_with_filter(staff_api_client, category):
    variables = {"name": category.name}
    response = staff_api_client.post_graphql(QUERY_CATEGORIES, variables=variables)
    content = get_graphql_content(response)
    data = content['data']['categories']
    global_id = graphene.Node.to_global_id("Category", category.pk)

    assert len(data['edges']) == 1
    assert data['edges'][0]['node']['id'] == global_id


CREATE_CATEGORY_MUTATION = """
    mutation CategoryCreate($input: CategoryInput!){
        categoryCreate(input: $input){
            category{
                id
                name
                slug
            }
            errors{
                message
                field
                code
            }
        }
    }
"""


def test_investment_create_mutation(staff_api_client, permission_manage_categories):
    input = {
        "name": "Category",
        "slug": "category"
    }
    variables = {"input": input}
    response = staff_api_client.post_graphql(
        CREATE_CATEGORY_MUTATION,
        permissions=[permission_manage_categories],
        variables=variables
    )
    content = get_graphql_content(response)
    data = content["data"]["categoryCreate"]
    assert data["errors"] == []
    assert data["category"]["name"] == input["name"]
    assert data["category"]["slug"] == input["slug"]


def test_category_create_mutation_missing_params(
    staff_api_client, permission_manage_categories
):
    input = {
        "slug": "category",
    }
    variables = {"input": input}
    response = staff_api_client.post_graphql(
        CREATE_CATEGORY_MUTATION,
        permissions=[permission_manage_categories],
        variables=variables
    )
    content = get_graphql_content(response)
    data = content["data"]["categoryCreate"]

    assert data['category'] is None
    assert data['errors'] is not None
    assert data['errors'][0]['field'] == "name"


UPDATE_CATEGORY_MUTATION = """
    mutation CategoryUpdate($id: ID, $input: CategoryInput!){
        categoryUpdate(id: $id, input: $input){
            category{
                id
                name
                slug
            }
            errors{
                message
                field
                code
            }
        }
    }
"""


def test_category_update_mutation(
    staff_api_client, permission_manage_categories, category
):
    category_id = graphene.Node.to_global_id("Category", category.pk)
    input = {
        "name": "New name"
    }
    variables = {
        "id": category_id,
        "input": input
    }
    response = staff_api_client.post_graphql(
        UPDATE_CATEGORY_MUTATION,
        permissions=[permission_manage_categories],
        variables=variables
    )
    content = get_graphql_content(response)
    data = content["data"]["categoryUpdate"]
    assert data["errors"] == []
    assert data["category"]["id"] == category_id
    assert data["category"]["name"] == input["name"]


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


def test_category_delete_mutation(
    staff_api_client, permission_manage_categories, category,
):
    category_id = graphene.Node.to_global_id("Category", category.id)
    variables = {"id": category_id}
    response = staff_api_client.post_graphql(
        CATEGORY_DELETE_MUTATION,
        variables=variables,
        permissions=[permission_manage_categories]
    )
    content = get_graphql_content(response)
    data = content["data"]["categoryDelete"]

    assert data["errors"] == []
    assert data["category"]["id"] == category_id


def test_category_delete_mutation_with_invalid_id(
    staff_api_client, permission_manage_categories, category,
):
    variables = {"id": "'"}
    response = staff_api_client.post_graphql(
        CATEGORY_DELETE_MUTATION,
        variables=variables,
        permissions=[permission_manage_categories]
    )
    content = get_graphql_content(response)
    data = content["data"]["categoryDelete"]

    assert data['category'] is None
    assert data['errors'] is not None
    assert data['errors'][0]['field'] == 'id'
