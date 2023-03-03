import graphene
import pytest

from portal.entry.models import Category, Entry

from ...tests.utils import get_graphql_content, get_graphql_content_from_response

pytestmark = pytest.mark.django_db

QUERY_ENTRY = """
    query ($id: ID, $slug: String){
        entry(
            id: $id,
            slug: $slug,
        ) {
            id
            name
            slug
            type
            isPublished
            category{
                id
                name
            }
            documents(first: 10){
                edges{
                    node{
                        id
                        name
                    }
                }
            }
        }
    }
"""


def test_entry_query_by_id(api_client, vehicle):
    variables = {"id": graphene.Node.to_global_id("Entry", vehicle.pk)}
    response = api_client.post_graphql(QUERY_ENTRY, variables=variables)
    content = get_graphql_content(response)
    data = content["data"]["entry"]
    assert data is not None
    assert data["name"] == vehicle.name


def test_entry_query_invalid_id(api_client, vehicle):
    entry_id = "'"
    variables = {"id": entry_id}
    response = api_client.post_graphql(QUERY_ENTRY, variables)
    content = get_graphql_content_from_response(response)
    assert len(content["errors"]) == 1
    assert content["errors"][0]["message"] == f"Couldn't resolve id: {entry_id}."
    assert content["data"]["entry"] is None


def test_entry_query_object_with_given_id_does_not_exist(api_client, vehicle):
    entry_id = graphene.Node.to_global_id("Entry", -1)
    variables = {"id": entry_id}
    response = api_client.post_graphql(QUERY_ENTRY, variables)
    content = get_graphql_content(response)
    assert content["data"]["entry"] is None


def test_entry_query_by_slug(api_client, vehicle):
    variables = {"slug": vehicle.slug}
    response = api_client.post_graphql(QUERY_ENTRY, variables=variables)
    content = get_graphql_content(response)
    data = content["data"]["entry"]
    assert data is not None
    assert data["name"] == vehicle.name


def test_entry_query_as_visitor(api_client, vehicle):
    vehicle.is_published = False
    vehicle.save()
    variables = {"id": graphene.Node.to_global_id("Entry", vehicle.pk)}
    response = api_client.post_graphql(QUERY_ENTRY, variables=variables)
    content = get_graphql_content(response)
    data = content["data"]["entry"]
    assert data is None


def test_entry_query_as_staff(staff_api_client, vehicle):
    vehicle.is_published = False
    vehicle.save()
    variables = {"id": graphene.Node.to_global_id("Entry", vehicle.pk)}
    response = staff_api_client.post_graphql(QUERY_ENTRY, variables=variables)
    content = get_graphql_content(response)
    data = content["data"]["entry"]
    assert data is not None
    assert data["name"] == vehicle.name


def test_entry_documents_as_visitor(api_client, vehicle, document_list):
    variables = {"id": graphene.Node.to_global_id("Entry", vehicle.pk)}
    response = api_client.post_graphql(QUERY_ENTRY, variables=variables)
    content = get_graphql_content(response)
    data = content["data"]["entry"]
    assert data is not None
    assert len(data["documents"]["edges"]) == len(document_list) - 1


def test_entry_documents_as_staff(staff_api_client, vehicle, document_list):
    variables = {"id": graphene.Node.to_global_id("Entry", vehicle.pk)}
    response = staff_api_client.post_graphql(QUERY_ENTRY, variables=variables)
    content = get_graphql_content(response)
    data = content["data"]["entry"]
    assert data is not None
    assert len(data["documents"]["edges"]) == len(document_list)
