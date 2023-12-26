import graphene
import pytest

from ....tests.utils import get_graphql_content, get_graphql_content_from_response

pytestmark = pytest.mark.django_db

QUERY_ENTRY_TYPE = """
    query ($id: ID, $slug: String){
        entryType (
            id: $id,
            slug: $slug,
        ) {
            id
            name
            slug
        }
    }
"""


def test_entry_type_query_by_id(api_client, entry_type):
    variables = {"id": graphene.Node.to_global_id("EntryType", entry_type.pk)}
    response = api_client.post_graphql(QUERY_ENTRY_TYPE, variables=variables)
    content = get_graphql_content(response)
    entry_type_data = content["data"]["entryType"]
    assert entry_type_data is not None
    assert entry_type_data["name"] == entry_type.name


def test_entry_type_query_invalid_id(api_client, entry_type):
    entry_type_id = "'"
    variables = {"id": entry_type_id}
    response = api_client.post_graphql(QUERY_ENTRY_TYPE, variables)
    content = get_graphql_content_from_response(response)
    assert len(content["errors"]) == 1
    assert content["errors"][0]["message"] == f"Couldn't resolve id: {entry_type_id}."
    assert content["data"]["entryType"] is None


def test_entry_type_query_object_with_given_id_does_not_exist(api_client, entry_type):
    entry_type_id = graphene.Node.to_global_id("EntryType", -1)
    variables = {"id": entry_type_id}
    response = api_client.post_graphql(QUERY_ENTRY_TYPE, variables)
    content = get_graphql_content(response)
    assert content["data"]["entryType"] is None


def test_entry_type_query_by_slug(api_client, entry_type):
    variables = {"slug": entry_type.slug}
    response = api_client.post_graphql(QUERY_ENTRY_TYPE, variables=variables)
    content = get_graphql_content(response)
    entry_type_data = content["data"]["entryType"]
    assert entry_type_data is not None
    assert entry_type_data["name"] == entry_type.name


QUERY_ENTRY_TYPES = """
    query ($first: Int, $sortBy: EntryTypeSortingInput){
        entryTypes(
            first: $first,
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


def test_entry_types(api_client, entry_type_list):
    variables = {"first": 10}
    response = api_client.post_graphql(QUERY_ENTRY_TYPES, variables=variables)
    content = get_graphql_content(response)
    data = content["data"]["entryTypes"]
    assert len(data["edges"]) == len(entry_type_list)


def test_entry_types_sorting(api_client, entry_type_list):
    variables = {
        "first": 10,
        "sortBy": {
            "field": "NAME",
            "direction": "DESC",
        },
    }
    response = api_client.post_graphql(QUERY_ENTRY_TYPES, variables=variables)
    last_id = graphene.Node.to_global_id("EntryType", entry_type_list[-1].pk)
    content = get_graphql_content(response)
    data = content["data"]["entryTypes"]
    assert data["edges"][0]["node"]["id"] == last_id
