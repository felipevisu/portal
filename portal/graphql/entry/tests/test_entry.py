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


QUERY_ENTRIES = """
    query ($first: Int, $filter: EntryFilterInput, $sortBy: EntrySortingInput){
        entries(
            first: $first,
            filter: $filter,
            sortBy: $sortBy
        ) {
            edges{
                node{
                    id
                    name
                    slug
                    isPublished
                    type
                    category{
                        id
                        name
                        slug
                    }
                }
            }
        }
    }
"""


def test_entries_as_visitor(api_client, vehicle_list):
    variables = {"first": 10}
    response = api_client.post_graphql(QUERY_ENTRIES, variables=variables)
    content = get_graphql_content(response)
    data = content["data"]["entries"]
    assert len(data["edges"]) == len(vehicle_list) - 1


def test_entries_as_staff(staff_api_client, vehicle_list):
    variables = {"first": 10}
    response = staff_api_client.post_graphql(QUERY_ENTRIES, variables=variables)
    content = get_graphql_content(response)
    data = content["data"]["entries"]
    assert len(data["edges"]) == len(vehicle_list)


def test_entries_sorting(api_client, vehicle_list):
    variables = {
        "first": 10,
        "sortBy": {
            "field": "NAME",
            "direction": "DESC",
        },
    }
    response = api_client.post_graphql(QUERY_ENTRIES, variables=variables)
    content = get_graphql_content(response)
    data = content["data"]["entries"]
    assert data["edges"][0]["node"]["name"] == "Vehicle 2"


def test_entries_search(api_client, vehicle_list):
    name = "Vehicle 2"
    variables = {
        "first": 10,
        "filter": {"search": name},
    }
    response = api_client.post_graphql(QUERY_ENTRIES, variables=variables)
    content = get_graphql_content(response)
    data = content["data"]["entries"]
    assert len(data["edges"]) == 1
    assert data["edges"][0]["node"]["name"] == name


def test_entries_filter_by_type(staff_api_client, vehicle_list, provider_list):
    variables = {"first": 10, "filter": {"type": "PROVIDER"}}
    response = staff_api_client.post_graphql(QUERY_ENTRIES, variables=variables)
    content = get_graphql_content(response)
    data = content["data"]["entries"]
    assert len(data["edges"]) == len(provider_list)


CREATE_ENTRY_MUTATION = """
    mutation EntryCreate($input: EntryInput!, $type: EntryTypeEnum){
        entryCreate(input: $input, type: $type){
            entry{
                id
                name
                slug
                email
                documentNumber
            }
            errors{
                message
                field
                code
            }
        }
    }
"""


def test_entry_create(staff_api_client, category, permission_manage_entries):
    category_id = graphene.Node.to_global_id("Category", category.pk)
    input = {
        "name": "Entry",
        "slug": "entry",
        "documentNumber": "123456789",
        "category": category_id,
        "email": "vehicle@email.com",
    }
    variables = {"input": input, "type": "VEHICLE"}
    response = staff_api_client.post_graphql(
        CREATE_ENTRY_MUTATION,
        variables=variables,
        permissions=[permission_manage_entries],
    )
    content = get_graphql_content(response)
    data = content["data"]["entryCreate"]
    assert not data["errors"]
    assert data["entry"]["name"] == input["name"]


def test_entry_create_without_slug(
    staff_api_client, category, permission_manage_entries
):
    category_id = graphene.Node.to_global_id("Category", category.pk)
    input = {
        "name": "Entry",
        "documentNumber": "123456789",
        "category": category_id,
        "email": "vehicle@email.com",
    }
    variables = {"input": input, "type": "VEHICLE"}
    response = staff_api_client.post_graphql(
        CREATE_ENTRY_MUTATION,
        variables=variables,
        permissions=[permission_manage_entries],
    )
    content = get_graphql_content(response)
    data = content["data"]["entryCreate"]
    assert not data["errors"]
    assert data["entry"]["name"] == input["name"]
    assert data["entry"]["slug"] == "entry"


def test_entry_create_without_category(staff_api_client, permission_manage_entries):
    input = {
        "name": "Entry",
        "documentNumber": "123456789",
        "email": "vehicle@email.com",
    }
    variables = {"input": input, "type": "VEHICLE"}
    response = staff_api_client.post_graphql(
        CREATE_ENTRY_MUTATION,
        variables=variables,
        permissions=[permission_manage_entries],
    )
    content = get_graphql_content(response)
    data = content["data"]["entryCreate"]
    assert data["errors"]
    assert data["errors"][0]["field"] == "category"


def test_entry_create_without_document(
    staff_api_client, category, permission_manage_entries
):
    category_id = graphene.Node.to_global_id("Category", category.pk)
    input = {
        "name": "Entry",
        "slug": "entry",
        "category": category_id,
        "email": "vehicle@email.com",
    }
    variables = {"input": input, "type": "VEHICLE"}
    response = staff_api_client.post_graphql(
        CREATE_ENTRY_MUTATION,
        variables=variables,
        permissions=[permission_manage_entries],
    )
    content = get_graphql_content(response)
    data = content["data"]["entryCreate"]
    assert data["errors"]
    assert data["errors"][0]["field"] == "documentNumber"


def test_entry_create_without_email(
    staff_api_client, category, permission_manage_entries
):
    category_id = graphene.Node.to_global_id("Category", category.pk)
    input = {
        "name": "Entry",
        "slug": "entry",
        "category": category_id,
        "documentNumber": "123456789",
    }
    variables = {"input": input, "type": "VEHICLE"}
    response = staff_api_client.post_graphql(
        CREATE_ENTRY_MUTATION,
        variables=variables,
        permissions=[permission_manage_entries],
    )
    content = get_graphql_content(response)
    data = content["data"]["entryCreate"]
    assert data["errors"]
    assert data["errors"][0]["field"] == "email"


UPDATE_ENTRY_MUTATION = """
    mutation EntryUpdate($id: ID!, $input: EntryInput!){
        entryUpdate(id: $id, input: $input){
            entry{
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


def test_entry_update(staff_api_client, vehicle, permission_manage_entries):
    input = {"name": "Entry Updated"}
    entry_id = graphene.Node.to_global_id("Entry", vehicle.pk)
    variables = {"id": entry_id, "input": input}
    response = staff_api_client.post_graphql(
        UPDATE_ENTRY_MUTATION,
        variables=variables,
        permissions=[permission_manage_entries],
    )
    vehicle.refresh_from_db()
    content = get_graphql_content(response)
    data = content["data"]["entryUpdate"]
    assert not data["errors"]
    assert vehicle.name == input["name"]


def test_entry_update_with_existent_slug(
    staff_api_client, vehicle, category, permission_manage_entries
):
    new_entry = Entry.objects.create(
        name="New Vehicle",
        slug="new-vehicle",
        category=category,
        type="vehicle",
        document_number="123456789",
    )
    input = {"slug": "new-vehicle"}
    entry_id = graphene.Node.to_global_id("Entry", vehicle.pk)
    variables = {"id": entry_id, "input": input}
    response = staff_api_client.post_graphql(
        UPDATE_ENTRY_MUTATION,
        variables=variables,
        permissions=[permission_manage_entries],
    )
    vehicle.refresh_from_db()
    content = get_graphql_content(response)
    data = content["data"]["entryUpdate"]
    assert data["errors"]
    assert data["errors"][0]["field"] == "slug"


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


def test_category_delete(
    staff_api_client,
    permission_manage_entries,
    vehicle,
):
    entry_id = graphene.Node.to_global_id("Entry", vehicle.id)
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


def test_entry_delete_with_invalid_id(
    staff_api_client,
    permission_manage_entries,
    vehicle,
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
