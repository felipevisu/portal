import graphene
import pytest

from portal.entry.models import EntryType

from ....tests.utils import get_graphql_content

pytestmark = pytest.mark.django_db


CREATE_ENTRY_TYPE_MUTATION = """
    mutation EntryTypeCreate($input: EntryTypeInput!){
        entryTypeCreate(input: $input){
            entryType{
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


def test_entry_type_create(staff_api_client, permission_manage_entry_types):
    input = {"name": "Entry Type", "slug": "entry-type"}
    variables = {"input": input}
    response = staff_api_client.post_graphql(
        CREATE_ENTRY_TYPE_MUTATION,
        variables=variables,
        permissions=[permission_manage_entry_types],
    )
    content = get_graphql_content(response)
    data = content["data"]["entryTypeCreate"]
    assert not data["errors"]
    assert data["entryType"]["name"] == input["name"]
    assert data["entryType"]["slug"] == input["slug"]


def test_entyr_type_create_without_slug(
    staff_api_client, permission_manage_entry_types
):
    input = {"name": "Entry Type"}
    variables = {"input": input}
    response = staff_api_client.post_graphql(
        CREATE_ENTRY_TYPE_MUTATION,
        variables=variables,
        permissions=[permission_manage_entry_types],
    )
    content = get_graphql_content(response)
    data = content["data"]["entryTypeCreate"]
    assert not data["errors"]
    assert data["entryType"]["name"] == input["name"]
    assert data["entryType"]["slug"] == "entry-type"


def test_entry_type_create_with_existent_name(
    staff_api_client, entry_type, permission_manage_entry_types
):
    input = {"name": "Entry Type"}
    variables = {"input": input}
    response = staff_api_client.post_graphql(
        CREATE_ENTRY_TYPE_MUTATION,
        variables=variables,
        permissions=[permission_manage_entry_types],
    )
    content = get_graphql_content(response)
    data = content["data"]["entryTypeCreate"]
    assert not data["errors"]
    assert data["entryType"]["name"] == input["name"]
    assert data["entryType"]["slug"] == "entry-type-2"


def test_entry_type_create_without_name(
    staff_api_client, permission_manage_entry_types
):
    input = {}
    variables = {"input": input}
    response = staff_api_client.post_graphql(
        CREATE_ENTRY_TYPE_MUTATION,
        variables=variables,
        permissions=[permission_manage_entry_types],
    )
    content = get_graphql_content(response)
    data = content["data"]["entryTypeCreate"]
    assert not data["errors"] == []
    assert data["errors"][0]["field"] == "name"


UPDATE_ENTRY_TYPE_MUTATION = """
    mutation EntryTypeUpdate($id: ID!, $input: EntryTypeInput!){
        entryTypeUpdate(id: $id, input: $input){
            entryType{
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


def test_entry_type_update(staff_api_client, entry_type, permission_manage_entry_types):
    input = {"name": "Entry Type Updated"}
    entry_type_id = graphene.Node.to_global_id("EntryType", entry_type.pk)
    variables = {"id": entry_type_id, "input": input}
    response = staff_api_client.post_graphql(
        UPDATE_ENTRY_TYPE_MUTATION,
        variables=variables,
        permissions=[permission_manage_entry_types],
    )
    entry_type.refresh_from_db()
    content = get_graphql_content(response)
    data = content["data"]["entryTypeUpdate"]
    assert not data["errors"]
    assert entry_type.name == input["name"]


def test_entry_type_update_with_existent_slug(
    staff_api_client, entry_type, permission_manage_entry_types
):
    new_entry_type = EntryType.objects.create(
        name="New Entry Type", slug="new-entry-type"
    )
    input = {"slug": "entry-type"}
    entry_type_id = graphene.Node.to_global_id("EntryType", new_entry_type.pk)
    variables = {"id": entry_type_id, "input": input}
    response = staff_api_client.post_graphql(
        UPDATE_ENTRY_TYPE_MUTATION,
        variables=variables,
        permissions=[permission_manage_entry_types],
    )
    entry_type.refresh_from_db()
    content = get_graphql_content(response)
    data = content["data"]["entryTypeUpdate"]
    assert data["errors"]
    assert data["errors"][0]["field"] == "slug"


ENTRY_TYPE_DELETE_MUTATION = """
    mutation($id: ID!) {
        entryTypeDelete(id: $id) {
            entryType{
                id
            }
            errors {
                field
                message
            }
        }
    }
"""


def test_entry_type_delete(staff_api_client, permission_manage_entry_types, entry_type):
    entry_type_id = graphene.Node.to_global_id("EntryType", entry_type.id)
    variables = {"id": entry_type_id}
    response = staff_api_client.post_graphql(
        ENTRY_TYPE_DELETE_MUTATION,
        variables=variables,
        permissions=[permission_manage_entry_types],
    )
    content = get_graphql_content(response)
    data = content["data"]["entryTypeDelete"]

    assert data["errors"] == []
    assert data["entryType"]["id"] == entry_type_id


def test_entry_type_delete_with_invalid_id(
    staff_api_client,
    permission_manage_entry_types,
    entry_type,
):
    variables = {"id": "'"}
    response = staff_api_client.post_graphql(
        ENTRY_TYPE_DELETE_MUTATION,
        variables=variables,
        permissions=[permission_manage_entry_types],
    )
    content = get_graphql_content(response)
    data = content["data"]["entryTypeDelete"]

    assert data["entryType"] is None
    assert data["errors"] is not None
    assert data["errors"][0]["field"] == "id"
