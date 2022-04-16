import pytest

from ...tests.utils import get_graphql_content

pytestmark = pytest.mark.django_db

MUTATION_TOKEN_AUTH = """
    mutation GenerateToken($email: String!, $password: String!){
        tokenAuth(email: $email, password: $password) {
            token
            user{
                id
                email
                firstName
                lastName
            }
            errors{
                message
                field
            }
        }
    }
"""


def test_create_token(api_client, user):
    variables = {"email": user.email, "password": user._password}
    response = api_client.post_graphql(
        MUTATION_TOKEN_AUTH,
        op_name='GenerateToken',
        variables=variables
    )
    content = get_graphql_content(response)
    data = content["data"]["tokenAuth"]
    email = data["user"]["email"]

    assert email == user.email


def test_create_token_invalid_password(api_client, user):
    variables = {"email": user.email, "password": "wrong"}
    response = api_client.post_graphql(
        MUTATION_TOKEN_AUTH,
        op_name='GenerateToken',
        variables=variables
    )
    content = get_graphql_content(response, ignore_errors=True)
    data = content["data"]["tokenAuth"]
    errors = data["errors"]
    message = errors[0]["message"]
    assert message == "Please enter valid credentials"
