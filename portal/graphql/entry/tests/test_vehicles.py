import graphene
import pytest

from ...tests.utils import get_graphql_content

pytestmark = pytest.mark.django_db

QUERY_ENTRY = """
    query Entry($id: ID, $slug: String) {
        entry(id: $id, slug: $slug) {
            id
            name
            slug
            category{
                id
                name
            }
        }
    }
"""

QUERY_ENTRIES = """
    query Entries($first: Int, $filter: EntryFilterInput){
        entries(first: $first, filter: $filter){
            edges{
                node{
                    id
                    name
                    slug
                    category{
                        id
                        name
                    }
                }
            }
        }
    }
"""


def test_entry_staff_query_by_id(staff_api_client, entry):
    entry_id = graphene.Node.to_global_id("Entry", entry.pk)
    variables = {"id": entry_id}
    response = staff_api_client.post_graphql(QUERY_ENTRY, variables=variables)
    content = get_graphql_content(response)
    data = content["data"]["entry"]

    assert data["id"] == entry_id
    assert data["name"] == entry.name
    assert data["slug"] == entry.slug


def test_entry_query_by_invalid_id(staff_api_client):
    entry_id = "'"
    variables = {"id": entry_id}
    response = staff_api_client.post_graphql(QUERY_ENTRY, variables=variables)
    content = get_graphql_content(response, ignore_errors=True)
    assert len(content["errors"]) == 1
    assert content["errors"][0]["message"] == f"Couldn't resolve id: {entry_id}."
    assert content["data"]["entry"] is None


def test_entry_staff_query_by_slug(staff_api_client, entry):
    variables = {"slug": entry.slug}
    response = staff_api_client.post_graphql(QUERY_ENTRY, variables=variables)
    content = get_graphql_content(response)
    data = content["data"]["entry"]

    assert data["name"] == entry.name
    assert data["slug"] == entry.slug


def test_entry_anonymouns_query_unpublished(api_client, entry):
    variables = {
        "id": graphene.Node.to_global_id("Entry", entry.pk),
    }
    response = api_client.post_graphql(QUERY_ENTRY, variables=variables)
    content = get_graphql_content(response)
    data = content["data"]["entry"]

    assert data is None


def test_entry_anonymouns_query_published(api_client, published_entry):
    entry_id = graphene.Node.to_global_id("Entry", published_entry.pk)
    variables = {"id": entry_id}
    response = api_client.post_graphql(QUERY_ENTRY, variables=variables)
    content = get_graphql_content(response)
    data = content["data"]["entry"]

    assert data["id"] == entry_id
    assert data["name"] == published_entry.name
    assert data["slug"] == published_entry.slug


def test_entries_anonymouns_query(api_client, entry, published_entry):
    variables = {"first": 10}
    response = api_client.post_graphql(QUERY_ENTRIES, variables=variables)
    content = get_graphql_content(response)
    data = content["data"]["entries"]
    global_id = graphene.Node.to_global_id("Entry", published_entry.pk)

    assert len(data["edges"]) == 1
    assert data["edges"][0]["node"]["id"] == global_id


def test_entries_staff_query(staff_api_client, entry, published_entry):
    variables = {"first": 10}
    response = staff_api_client.post_graphql(QUERY_ENTRIES, variables=variables)
    content = get_graphql_content(response)
    data = content["data"]["entries"]

    assert len(data["edges"]) == 2


def test_entries_staff_query_with_filter(staff_api_client, entry, published_entry):
    variables = {"first": 10, "filter": {"isPublished": False}}
    response = staff_api_client.post_graphql(QUERY_ENTRIES, variables=variables)
    content = get_graphql_content(response)
    data = content["data"]["entries"]
    global_id = graphene.Node.to_global_id("Entry", entry.pk)

    assert len(data["edges"]) == 1
    assert data["edges"][0]["node"]["id"] == global_id


CREATE_ENTRY_MUTATION = """
    mutation EntryCreate($input: EntryInput!){
        entryCreate(input: $input){
            entry{
                id
                name
                slug
                category{
                    id
                    name
                }
            }
            errors{
                message
                field
                code
            }
        }
    }
"""


def test_entry_create_mutation(staff_api_client, category, permission_manage_entries):
    category_id = graphene.Node.to_global_id("Category", category.pk)
    input = {
        "name": "New entry",
        "slug": "new-entry",
        "documentNumber": "123456789",
        "category": category_id,
    }
    variables = {"input": input}
    response = staff_api_client.post_graphql(
        CREATE_ENTRY_MUTATION,
        permissions=[permission_manage_entries],
        variables=variables,
    )
    content = get_graphql_content(response)
    data = content["data"]["entryCreate"]

    assert data["errors"] == []
    assert data["entry"]["name"] == input["name"]
    assert data["entry"]["slug"] == input["slug"]
    assert data["entry"]["category"]["id"] == category_id


def test_entry_create_mutation_missing_params(
    staff_api_client, category, permission_manage_entries
):
    category_id = graphene.Node.to_global_id("Category", category.pk)
    input = {"name": "New entry", "slug": "new-entry", "category": category_id}
    variables = {"input": input}
    response = staff_api_client.post_graphql(
        CREATE_ENTRY_MUTATION,
        permissions=[permission_manage_entries],
        variables=variables,
    )
    content = get_graphql_content(response)
    data = content["data"]["entryCreate"]

    assert data["entry"] is None
    assert data["errors"] is not None
    assert data["errors"][0]["field"] == "documentNumber"


ENTRY_DELETE_MUTATION = """
    mutation($id: ID!) {
        entryDelete(id: $id) {
            entry {
                id
            }
            errors {
                field
                message
            }
        }
    }
"""


def test_entry_delete_mutation(
    staff_api_client,
    permission_manage_entries,
    entry,
):
    entry_id = graphene.Node.to_global_id("Entry", entry.id)
    variables = {"id": entry_id}
    response = staff_api_client.post_graphql(
        ENTRY_DELETE_MUTATION,
        variables=variables,
        permissions=[permission_manage_entries],
    )
    content = get_graphql_content(response)
    data = content["data"]["entryDelete"]

    assert data["errors"] == []
    assert data["entry"]["id"] == entry_id


def test_entry_delete_mutation_with_invalid_id(
    staff_api_client,
    permission_manage_entries,
    entry,
):
    variables = {"id": "'"}
    response = staff_api_client.post_graphql(
        ENTRY_DELETE_MUTATION,
        variables=variables,
        permissions=[permission_manage_entries],
    )
    content = get_graphql_content(response)
    data = content["data"]["entryDelete"]

    assert data["entry"] is None
    assert data["errors"] is not None
    assert data["errors"][0]["field"] == "id"
