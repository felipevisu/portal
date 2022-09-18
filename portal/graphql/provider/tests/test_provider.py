import graphene
import pytest

from portal.graphql.tests.utils import get_graphql_content

pytestmark = pytest.mark.django_db

QUERY_PROVIDER = """
    query Provider($id: ID, $slug: String) {
        provider(id: $id, slug: $slug) {
            id
            name
            slug
            segment{
                id
                name
            }
        }
    }
"""

QUERY_PROVIDERS = """
    query Providers($first: Int, $filter: ProviderFilterInput){
        providers(first: $first, filter: $filter){
            edges{
                node{
                    id
                    name
                    slug
                    segment{
                        id
                        name
                    }
                }
            }
        }
    }
"""


def test_provider_staff_query_by_id(staff_api_client, provider):
    provider_id = graphene.Node.to_global_id("Provider", provider.pk)
    variables = {"id": provider_id}
    response = staff_api_client.post_graphql(QUERY_PROVIDER, variables=variables)
    content = get_graphql_content(response)
    data = content['data']['provider']

    assert data['id'] == provider_id
    assert data['name'] == provider.name
    assert data['slug'] == provider.slug


def test_provider_query_by_invalid_id(staff_api_client):
    provider_id = "'"
    variables = {"id": provider_id}
    response = staff_api_client.post_graphql(QUERY_PROVIDER, variables=variables)
    content = get_graphql_content(response, ignore_errors=True)
    assert len(content["errors"]) == 1
    assert content["errors"][0]["message"] == f"Couldn't resolve id: {provider_id}."
    assert content["data"]["provider"] is None


def test_provider_staff_query_by_slug(staff_api_client, provider):
    variables = {"slug": provider.slug}
    response = staff_api_client.post_graphql(QUERY_PROVIDER, variables=variables)
    content = get_graphql_content(response)
    data = content['data']['provider']

    assert data['name'] == provider.name
    assert data['slug'] == provider.slug


def test_provider_anonymouns_query_unpublished(api_client, provider):
    variables = {
        "id": graphene.Node.to_global_id("Provider", provider.pk),
    }
    response = api_client.post_graphql(QUERY_PROVIDER, variables=variables)
    content = get_graphql_content(response)
    data = content['data']['provider']

    assert data is None


def test_provider_anonymouns_query_published(api_client, published_provider):
    provider_id = graphene.Node.to_global_id("Provider", published_provider.pk)
    variables = {"id": provider_id}
    response = api_client.post_graphql(QUERY_PROVIDER, variables=variables)
    content = get_graphql_content(response)
    data = content['data']['provider']

    assert data['id'] == provider_id
    assert data['name'] == published_provider.name
    assert data['slug'] == published_provider.slug


def test_providers_anonymouns_query(api_client, provider, published_provider):
    variables = {"first": 10}
    response = api_client.post_graphql(QUERY_PROVIDERS, variables=variables)
    content = get_graphql_content(response)
    data = content['data']['providers']
    global_id = graphene.Node.to_global_id("Provider", published_provider.pk)

    assert len(data['edges']) == 1
    assert data['edges'][0]['node']['id'] == global_id


def test_providers_staff_query(staff_api_client, provider, published_provider):
    variables = {"first": 10}
    response = staff_api_client.post_graphql(QUERY_PROVIDERS, variables=variables)
    content = get_graphql_content(response)
    data = content['data']['providers']

    assert len(data['edges']) == 2


def test_providers_staff_query_with_filter(
    staff_api_client, provider, published_provider
):
    variables = {"first": 10, "filter": {"isPublished": False}}
    response = staff_api_client.post_graphql(QUERY_PROVIDERS, variables=variables)
    content = get_graphql_content(response)
    data = content['data']['providers']
    global_id = graphene.Node.to_global_id("Provider", provider.pk)

    assert len(data['edges']) == 1
    assert data['edges'][0]['node']['id'] == global_id


CREATE_PROVIDER_MUTATION = """
    mutation ProviderCreate($input: ProviderInput!){
        providerCreate(input: $input){
            provider{
                id
                name
                slug
                segment{
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


def test_provider_create_mutation(
    staff_api_client, segment, permission_manage_providers
):
    segment_id = graphene.Node.to_global_id("Segment", segment.pk)
    input = {
        "name": "New provider",
        "slug": "new-provider",
        "documentNumber": "123456789",
        "segment": segment_id
    }
    variables = {"input": input}
    response = staff_api_client.post_graphql(
        CREATE_PROVIDER_MUTATION,
        permissions=[permission_manage_providers],
        variables=variables
    )
    content = get_graphql_content(response)
    data = content["data"]["providerCreate"]

    assert data["errors"] == []
    assert data["provider"]["name"] == input["name"]
    assert data["provider"]["slug"] == input["slug"]
    assert data["provider"]["segment"]["id"] == segment_id


def test_provider_create_mutation_missing_params(
    staff_api_client, segment, permission_manage_providers
):
    segment_id = graphene.Node.to_global_id("Segment", segment.pk)
    input = {
        "name": "New provider",
        "slug": "new-provider",
        "segment": segment_id
    }
    variables = {"input": input}
    response = staff_api_client.post_graphql(
        CREATE_PROVIDER_MUTATION,
        permissions=[permission_manage_providers],
        variables=variables
    )
    content = get_graphql_content(response)
    data = content["data"]["providerCreate"]

    assert data['provider'] is None
    assert data['errors'] is not None
    assert data['errors'][0]['field'] == "documentNumber"


PROVIDER_DELETE_MUTATION = """
    mutation($id: ID!) {
        providerDelete(id: $id) {
            provider {
                id
            }
            errors {
                field
                message
            }
        }
    }
"""


def test_provider_delete_mutation(
    staff_api_client, permission_manage_providers, provider,
):
    provider_id = graphene.Node.to_global_id("Provider", provider.id)
    variables = {"id": provider_id}
    response = staff_api_client.post_graphql(
        PROVIDER_DELETE_MUTATION,
        variables=variables,
        permissions=[permission_manage_providers]
    )
    content = get_graphql_content(response)
    data = content["data"]["providerDelete"]

    assert data["errors"] == []
    assert data["provider"]["id"] == provider_id


def test_provider_delete_mutation_with_invalid_id(
    staff_api_client, permission_manage_providers, provider,
):
    variables = {"id": "'"}
    response = staff_api_client.post_graphql(
        PROVIDER_DELETE_MUTATION,
        variables=variables,
        permissions=[permission_manage_providers]
    )
    content = get_graphql_content(response)
    data = content["data"]["providerDelete"]

    assert data['provider'] is None
    assert data['errors'] is not None
    assert data['errors'][0]['field'] == 'id'
