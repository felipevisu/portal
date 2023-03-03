import graphene
import pytest

from portal.entry.models import Category, Entry

from ...tests.utils import get_graphql_content, get_graphql_content_from_response

pytestmark = pytest.mark.django_db

QUERY_CATEGORY = """
    query ($id: ID, $slug: String){
        category(
            id: $id,
            slug: $slug,
        ) {
            id
            name
            slug
            entries(first: 10){
                edges{
                    node{
                        id
                        name
                        type
                    }
                }
            }
        }
    }
"""


def test_category_query_by_id(api_client, category):
    variables = {"id": graphene.Node.to_global_id("Category", category.pk)}
    response = api_client.post_graphql(QUERY_CATEGORY, variables=variables)
    content = get_graphql_content(response)
    category_data = content["data"]["category"]
    assert category_data is not None
    assert category_data["name"] == category.name


def test_category_query_invalid_id(api_client, category):
    category_id = "'"
    variables = {"id": category_id}
    response = api_client.post_graphql(QUERY_CATEGORY, variables)
    content = get_graphql_content_from_response(response)
    assert len(content["errors"]) == 1
    assert content["errors"][0]["message"] == f"Couldn't resolve id: {category_id}."
    assert content["data"]["category"] is None


def test_category_query_object_with_given_id_does_not_exist(api_client, category):
    category_id = graphene.Node.to_global_id("Category", -1)
    variables = {"id": category_id}
    response = api_client.post_graphql(QUERY_CATEGORY, variables)
    content = get_graphql_content(response)
    assert content["data"]["category"] is None


def test_category_query_by_slug(api_client, category):
    variables = {"slug": category.slug}
    response = api_client.post_graphql(QUERY_CATEGORY, variables=variables)
    content = get_graphql_content(response)
    category_data = content["data"]["category"]
    assert category_data is not None
    assert category_data["name"] == category.name


def test_query_category_entries_as_visitor(api_client, vehicle_list):
    category = Category.objects.first()
    published_vehicles = Entry.objects.published().count()
    variables = {"id": graphene.Node.to_global_id("Category", category.pk)}
    response = api_client.post_graphql(QUERY_CATEGORY, variables=variables)
    content = get_graphql_content(response, ignore_errors=True)
    assert len(content["data"]["category"]["entries"]["edges"]) == published_vehicles


def test_query_category_entries_as_staff(staff_api_client, vehicle_list):
    category = Category.objects.first()
    variables = {"id": graphene.Node.to_global_id("Category", category.pk)}
    response = staff_api_client.post_graphql(QUERY_CATEGORY, variables=variables)
    content = get_graphql_content(response, ignore_errors=True)
    assert len(content["data"]["category"]["entries"]["edges"]) == len(vehicle_list)


QUERY_CATEGORIES = """
    query ($first: Int, $filter: CategoryFilterInput, $sortBy: CategorySortingInput){
        categories(
            first: $first,
            filter: $filter,
            sortBy: $sortBy
        ) {
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


def test_categoryies(api_client, category_list):
    variables = {"first": 10}
    response = api_client.post_graphql(QUERY_CATEGORIES, variables=variables)
    content = get_graphql_content(response)
    data = content["data"]["categories"]
    assert len(data["edges"]) == len(category_list)


def test_categories_sorting(api_client, category_list):
    variables = {
        "first": 10,
        "sortBy": {
            "field": "NAME",
            "direction": "DESC",
        },
    }
    response = api_client.post_graphql(QUERY_CATEGORIES, variables=variables)
    last_id = graphene.Node.to_global_id("Category", category_list[-1].pk)
    content = get_graphql_content(response)
    data = content["data"]["categories"]
    assert data["edges"][0]["node"]["id"] == last_id


def test_categories_search(api_client, category_list):
    name = "Category 2"
    variables = {
        "first": 10,
        "filter": {"search": name},
    }
    response = api_client.post_graphql(QUERY_CATEGORIES, variables=variables)
    content = get_graphql_content(response)
    data = content["data"]["categories"]
    assert len(data["edges"]) == 1
    assert data["edges"][0]["node"]["name"] == name


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


def test_category_create(staff_api_client, permission_manage_categories):
    input = {"name": "Category", "slug": "category"}
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
    input = {"name": "Category"}
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
    input = {"name": "Category"}
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
    input = {}
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


UPDATE_CATEGORY_MUTATION = """
    mutation CategoryUpdate($id: ID!, $input: CategoryInput!){
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
    new_category = Category.objects.create(name="New Category", slug="new-category")
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
