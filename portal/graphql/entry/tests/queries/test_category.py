import graphene
import pytest

from ....tests.utils import get_graphql_content, get_graphql_content_from_response

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
            totalEntries
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
