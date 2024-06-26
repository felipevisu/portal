import json

import pytest
from django.contrib.auth.models import AnonymousUser
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import reverse
from django.test.client import MULTIPART_CONTENT, Client

from portal.core.jwt import create_access_token

from ...tests.utils import flush_post_commit_hooks
from .utils import assert_no_permission

API_PATH = reverse("api")


class ApiClient(Client):
    """GraphQL API client."""

    def __init__(self, client, user=None, *args, **kwargs):
        self._user = None
        self.token = None
        self.user = user
        if user:
            self.token = create_access_token(user)
        super().__init__(*args, **kwargs)

    def _base_environ(self, **request):
        environ = super()._base_environ(**request)
        if self.user:
            environ["HTTP_AUTHORIZATION"] = f"JWT {self.token}"
        return environ

    @property
    def user(self):
        return self._user

    @user.setter
    def user(self, user):
        self._user = user
        if user:
            self.token = create_access_token(user)

    def post(self, data=None, **kwargs):
        """Send a POST request.
        This wrapper sets the `application/json` content type which is
        more suitable for standard GraphQL requests and doesn't mismatch with
        handling multipart requests in Graphene.
        """
        if data:
            data = json.dumps(data, cls=DjangoJSONEncoder)
        kwargs["content_type"] = "application/json"
        return super().post(API_PATH, data, **kwargs)

    def post_graphql(
        self,
        query,
        variables=None,
        permissions=None,
        check_no_permissions=True,
        **kwargs,
    ):
        """Dedicated helper for posting GraphQL queries.
        Sets the `application/json` content type and json.dumps the variables
        if present.
        """
        data = {"query": query}
        if variables is not None:
            data["variables"] = variables
        if data:
            data = json.dumps(data, cls=DjangoJSONEncoder)
        kwargs["content_type"] = "application/json"

        if permissions:
            self.user.user_permissions.add(*permissions)
        result = super().post(API_PATH, data, **kwargs)
        flush_post_commit_hooks()
        return result

    def post_multipart(self, *args, permissions=None, **kwargs):
        """Send a multipart POST request.
        This is used to send multipart requests to GraphQL API when e.g.
        uploading files.
        """
        kwargs["content_type"] = MULTIPART_CONTENT

        if permissions:
            response = super().post(API_PATH, *args, **kwargs)
            assert_no_permission(response)
            self.user.user_permissions.add(*permissions)
        return super().post(API_PATH, *args, **kwargs)


@pytest.fixture
def api_client(client):
    return ApiClient(client)


@pytest.fixture
def staff_api_client(staff_user, client):
    return ApiClient(client, staff_user)


@pytest.fixture
def admin_api_client(admin_user, client):
    return ApiClient(client, admin_user)


@pytest.fixture
def superuser_api_client(superuser):
    return ApiClient(user=superuser)
