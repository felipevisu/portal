import json

from django.core.serializers.json import DjangoJSONEncoder


def get_graphql_content_from_response(response):
    return json.loads(response.content.decode("utf8"))


def get_graphql_content(response, *, ignore_errors: bool = False):
    content = get_graphql_content_from_response(response)
    if not ignore_errors:
        assert "errors" not in content, content["errors"]
    return content


def assert_no_permission(response):
    content = get_graphql_content_from_response(response)
    assert "errors" in content, content
    assert content["errors"][0]["message"] == (
        "You do not have permission to perform this action"
    ), content["errors"]


def get_multipart_request_body(query, variables, file, file_name):
    """Create request body for multipart GraphQL requests.

    Multipart requests are different from standard GraphQL requests, because
    of additional 'operations' and 'map' keys.
    """
    return {
        "operations": json.dumps(
            {"query": query, "variables": variables}, cls=DjangoJSONEncoder
        ),
        "map": json.dumps({file_name: ["variables.file"]}, cls=DjangoJSONEncoder),
        file_name: file,
    }
