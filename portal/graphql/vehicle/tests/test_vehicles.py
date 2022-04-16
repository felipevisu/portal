import graphene
import pytest

from ...tests.utils import get_graphql_content

pytestmark = pytest.mark.django_db

QUERY_VEHICLE = """
    query Vehicle($id: ID, $slug: String) {
        vehicle(id: $id, slug: $slug) {
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

QUERY_VEHICLES = """
    query Vehicles($isPublished: Boolean){
        vehicles(isPublished: $isPublished){
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


def test_vehicle_staff_query_by_id(staff_api_client, vehicle):
    vehicle_id = graphene.Node.to_global_id("Vehicle", vehicle.pk)
    variables = {"id": vehicle_id}
    response = staff_api_client.post_graphql(QUERY_VEHICLE, variables=variables)
    content = get_graphql_content(response)
    data = content['data']['vehicle']

    assert data['id'] == vehicle_id
    assert data['name'] == vehicle.name
    assert data['slug'] == vehicle.slug


def test_vehicle_query_by_invalid_id(staff_api_client):
    vehicle_id = "'"
    variables = {"id": vehicle_id}
    response = staff_api_client.post_graphql(QUERY_VEHICLE, variables=variables)
    content = get_graphql_content(response, ignore_errors=True)
    assert len(content["errors"]) == 1
    assert content["errors"][0]["message"] == f"Couldn't resolve id: {vehicle_id}."
    assert content["data"]["vehicle"] is None


def test_vehicle_staff_query_by_slug(staff_api_client, vehicle):
    variables = {"slug": vehicle.slug}
    response = staff_api_client.post_graphql(QUERY_VEHICLE, variables=variables)
    content = get_graphql_content(response)
    data = content['data']['vehicle']

    assert data['name'] == vehicle.name
    assert data['slug'] == vehicle.slug


def test_vehicle_anonymouns_query_unpublished(api_client, vehicle):
    variables = {
        "id": graphene.Node.to_global_id("Vehicle", vehicle.pk),
    }
    response = api_client.post_graphql(QUERY_VEHICLE, variables=variables)
    content = get_graphql_content(response)
    data = content['data']['vehicle']

    assert data is None


def test_vehicle_anonymouns_query_published(api_client, published_vehicle):
    vehicle_id = graphene.Node.to_global_id("Vehicle", published_vehicle.pk)
    variables = {"id": vehicle_id}
    response = api_client.post_graphql(QUERY_VEHICLE, variables=variables)
    content = get_graphql_content(response)
    data = content['data']['vehicle']

    assert data['id'] == vehicle_id
    assert data['name'] == published_vehicle.name
    assert data['slug'] == published_vehicle.slug


def test_vehicles_anonymouns_query(api_client, vehicle, published_vehicle):
    response = api_client.post_graphql(QUERY_VEHICLES)
    content = get_graphql_content(response)
    data = content['data']['vehicles']
    global_id = graphene.Node.to_global_id("Vehicle", published_vehicle.pk)

    assert len(data['edges']) == 1
    assert data['edges'][0]['node']['id'] == global_id


def test_vehicles_staff_query(staff_api_client, vehicle, published_vehicle):
    response = staff_api_client.post_graphql(QUERY_VEHICLES)
    content = get_graphql_content(response)
    data = content['data']['vehicles']

    assert len(data['edges']) == 2


def test_vehicles_staff_query_with_filter(
    staff_api_client, vehicle, published_vehicle
):
    variables = {"isPublished": False, }
    response = staff_api_client.post_graphql(QUERY_VEHICLES, variables=variables)
    content = get_graphql_content(response)
    data = content['data']['vehicles']
    global_id = graphene.Node.to_global_id("Vehicle", vehicle.pk)

    assert len(data['edges']) == 1
    assert data['edges'][0]['node']['id'] == global_id


CREATE_VEHICLE_MUTATION = """
    mutation VehicleCreate($input: VehicleInput!){
        vehicleCreate(input: $input){
            vehicle{
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


def test_vehicle_create_mutation(
    staff_api_client, category, permission_manage_vehicles
):
    category_id = graphene.Node.to_global_id("Category", category.pk)
    input = {
        "name": "New vehicle",
        "slug": "new-vehicle",
        "documentNumber": "123456789",
        "category": category_id
    }
    variables = {"input": input}
    response = staff_api_client.post_graphql(
        CREATE_VEHICLE_MUTATION,
        permissions=[permission_manage_vehicles],
        variables=variables
    )
    content = get_graphql_content(response)
    data = content["data"]["vehicleCreate"]

    assert data["errors"] == []
    assert data["vehicle"]["name"] == input["name"]
    assert data["vehicle"]["slug"] == input["slug"]
    assert data["vehicle"]["category"]["id"] == category_id


def test_vehicle_create_mutation_missing_params(
    staff_api_client, category, permission_manage_vehicles
):
    category_id = graphene.Node.to_global_id("Category", category.pk)
    input = {
        "name": "New vehicle",
        "slug": "new-vehicle",
        "category": category_id
    }
    variables = {"input": input}
    response = staff_api_client.post_graphql(
        CREATE_VEHICLE_MUTATION,
        permissions=[permission_manage_vehicles],
        variables=variables
    )
    content = get_graphql_content(response)
    data = content["data"]["vehicleCreate"]

    assert data['vehicle'] is None
    assert data['errors'] is not None
    assert data['errors'][0]['field'] == "documentNumber"


VEHICLE_DELETE_MUTATION = """
    mutation($id: ID!) {
        vehicleDelete(id: $id) {
            vehicle {
                id
            }
            errors {
                field
                message
            }
        }
    }
"""


def test_vehicle_delete_mutation(
    staff_api_client, permission_manage_vehicles, vehicle,
):
    vehicle_id = graphene.Node.to_global_id("Vehicle", vehicle.id)
    variables = {"id": vehicle_id}
    response = staff_api_client.post_graphql(
        VEHICLE_DELETE_MUTATION,
        variables=variables,
        permissions=[permission_manage_vehicles]
    )
    content = get_graphql_content(response)
    data = content["data"]["vehicleDelete"]

    assert data["errors"] == []
    assert data["vehicle"]["id"] == vehicle_id


def test_vehicle_delete_mutation_with_invalid_id(
    staff_api_client, permission_manage_vehicles, vehicle,
):
    variables = {"id": "'"}
    response = staff_api_client.post_graphql(
        VEHICLE_DELETE_MUTATION,
        variables=variables,
        permissions=[permission_manage_vehicles]
    )
    content = get_graphql_content(response)
    data = content["data"]["vehicleDelete"]

    assert data['vehicle'] is None
    assert data['errors'] is not None
    assert data['errors'][0]['field'] == 'id'
