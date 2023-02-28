import pytest
from django.contrib.auth.models import AnonymousUser
from graphene_django.utils.testing import graphql_query

from portal.core.jwt import create_access_token


class ApiClient:
    def __init__(self, client, user=AnonymousUser(), *args, **kwargs):
        self.user = user
        self.client = client
        self.token = None
        self.headers = {}

        if not user.is_anonymous:
            self.token = create_access_token(user)
            self.headers["HTTP_AUTHORIZATION"] = f"JWT {self.token}"

    def post_graphql(self, *args, **kwargs):
        if "permissions" in kwargs:
            permissions = kwargs.pop("permissions")
            if self.user:
                self.user.user_permissions.add(*permissions)
                self.user.save()
        return graphql_query(*args, **kwargs, headers=self.headers, client=self.client)


@pytest.fixture
def api_client(client):
    return ApiClient(client)


@pytest.fixture
def user_api_client(user, client):
    return ApiClient(client, user)


@pytest.fixture
def staff_api_client(staff_user, client):
    return ApiClient(client, staff_user)
