import pytest

from ...tests.utils import get_graphql_content

pytestmark = pytest.mark.django_db

ME_QUERY = """
    query Me {
        me {
            id
            email
        }
    }
"""


def test_me_query(user_api_client):
    response = user_api_client.post_graphql(ME_QUERY)
    content = get_graphql_content(response)
    data = content["data"]["me"]
    assert data["email"] == user_api_client.user.email
