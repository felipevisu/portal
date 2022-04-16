import graphene
import pytest

from ...tests.utils import get_graphql_content

pytestmark = pytest.mark.django_db

QUERY_SEGMENT = """
    query Segment($id: ID, $slug: String) {
        segment(id: $id, slug: $slug) {
            id
            name
            slug
        }
    }
"""

QUERY_SEGMENTS = """
    query Segments{
        segments{
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


def test_segment_query_by_id(api_client, segment):
    segment_id = graphene.Node.to_global_id("Segment", segment.pk)
    variables = {"id": segment_id}
    response = api_client.post_graphql(QUERY_SEGMENT, variables=variables)
    content = get_graphql_content(response)
    data = content['data']['segment']

    assert data['id'] == segment_id
    assert data['name'] == segment.name
    assert data['slug'] == segment.slug


def test_segment_query_by_slug(api_client, segment):
    variables = {"slug": segment.slug}
    response = api_client.post_graphql(QUERY_SEGMENT, variables=variables)
    content = get_graphql_content(response)
    data = content['data']['segment']

    assert data['name'] == segment.name
    assert data['slug'] == segment.slug


def test_segment_query_by_invalid_id(api_client):
    segment_id = "'"
    variables = {"id": segment_id}
    response = api_client.post_graphql(QUERY_SEGMENT, variables=variables)
    content = get_graphql_content(response, ignore_errors=True)
    assert len(content["errors"]) == 1
    assert content["errors"][0]["message"] == f"Couldn't resolve id: {segment_id}."
    assert content["data"]["segment"] is None


def test_segments_query(api_client, segment):
    response = api_client.post_graphql(QUERY_SEGMENTS)
    content = get_graphql_content(response, ignore_errors=True)
    data = content['data']['segments']
    global_id = graphene.Node.to_global_id("Segment", segment.pk)

    assert len(data['edges']) == 1
    assert data['edges'][0]['node']['id'] == global_id


def test_segments_query_with_filter(staff_api_client, segment):
    variables = {"name": segment.name}
    response = staff_api_client.post_graphql(QUERY_SEGMENTS, variables=variables)
    content = get_graphql_content(response)
    data = content['data']['segments']
    global_id = graphene.Node.to_global_id("Segment", segment.pk)

    assert len(data['edges']) == 1
    assert data['edges'][0]['node']['id'] == global_id


CREATE_SEGMENT_MUTATION = """
    mutation SegmentCreate($input: SegmentInput!){
        segmentCreate(input: $input){
            segment{
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


def test_investment_create_mutation(staff_api_client, permission_manage_segments):
    input = {
        "name": "Segment",
        "slug": "segment"
    }
    variables = {"input": input}
    response = staff_api_client.post_graphql(
        CREATE_SEGMENT_MUTATION,
        permissions=[permission_manage_segments],
        variables=variables
    )
    content = get_graphql_content(response)
    data = content["data"]["segmentCreate"]
    assert data["errors"] == []
    assert data["segment"]["name"] == input["name"]
    assert data["segment"]["slug"] == input["slug"]


def test_segment_create_mutation_missing_params(
    staff_api_client, permission_manage_segments
):
    input = {
        "slug": "segment",
    }
    variables = {"input": input}
    response = staff_api_client.post_graphql(
        CREATE_SEGMENT_MUTATION,
        permissions=[permission_manage_segments],
        variables=variables
    )
    content = get_graphql_content(response)
    data = content["data"]["segmentCreate"]

    assert data['segment'] is None
    assert data['errors'] is not None
    assert data['errors'][0]['field'] == "name"


UPDATE_SEGMENT_MUTATION = """
    mutation SegmentUpdate($id: ID, $input: SegmentInput!){
        segmentUpdate(id: $id, input: $input){
            segment{
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


def test_segment_update_mutation(
    staff_api_client, permission_manage_segments, segment
):
    segment_id = graphene.Node.to_global_id("Segment", segment.pk)
    input = {
        "name": "New name"
    }
    variables = {
        "id": segment_id,
        "input": input
    }
    response = staff_api_client.post_graphql(
        UPDATE_SEGMENT_MUTATION,
        permissions=[permission_manage_segments],
        variables=variables
    )
    content = get_graphql_content(response)
    data = content["data"]["segmentUpdate"]
    assert data["errors"] == []
    assert data["segment"]["id"] == segment_id
    assert data["segment"]["name"] == input["name"]


SEGMENT_DELETE_MUTATION = """
    mutation($id: ID!) {
        segmentDelete(id: $id) {
            segment {
                id
            }
            errors {
                field
                message
            }
        }
    }
"""


def test_segment_delete_mutation(
    staff_api_client, permission_manage_segments, segment,
):
    segment_id = graphene.Node.to_global_id("Segment", segment.id)
    variables = {"id": segment_id}
    response = staff_api_client.post_graphql(
        SEGMENT_DELETE_MUTATION,
        variables=variables,
        permissions=[permission_manage_segments]
    )
    content = get_graphql_content(response)
    data = content["data"]["segmentDelete"]

    assert data["errors"] == []
    assert data["segment"]["id"] == segment_id


def test_segment_delete_mutation_with_invalid_id(
    staff_api_client, permission_manage_segments, segment,
):
    variables = {"id": "'"}
    response = staff_api_client.post_graphql(
        SEGMENT_DELETE_MUTATION,
        variables=variables,
        permissions=[permission_manage_segments]
    )
    content = get_graphql_content(response)
    data = content["data"]["segmentDelete"]

    assert data['segment'] is None
    assert data['errors'] is not None
    assert data['errors'][0]['field'] == 'id'
