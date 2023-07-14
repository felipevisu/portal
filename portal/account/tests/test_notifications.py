import pytest
from unittest import mock
from urllib.parse import urlencode

from portal.core.notify_events import NotifyEventType
from ...graphql.core.utils import to_global_id_or_none
from ..notifications import get_default_user_payload, send_password_reset_notification
from ...core.url import prepare_url
from ...plugins.manager import get_plugins_manager

pytestmark = pytest.mark.django_db


def test_get_default_user_payload(staff_user):
    assert get_default_user_payload(staff_user) == {
        "id": to_global_id_or_none(staff_user),
        "email": staff_user.email,
        "first_name": staff_user.first_name,
        "last_name": staff_user.last_name,
        "is_staff": staff_user.is_staff,
        "is_active": staff_user.is_active,
    }


@mock.patch("portal.account.notifications.default_token_generator.make_token")
@mock.patch("portal.plugins.manager.PluginsManager.notify")
def test_send_password_reset_notification(mocked_notify, mocked_generator, staff_user):
    token = "token_example"
    mocked_generator.return_value = token
    redirect_url = "http://localhost:8000/reset"
    params = urlencode({"email": staff_user.email, "token": token})
    reset_url = prepare_url(params, redirect_url)

    send_password_reset_notification(staff_user, redirect_url, get_plugins_manager())

    expected_payload = {
        "user": get_default_user_payload(staff_user),
        "recipient_email": staff_user.email,
        "token": token,
        "reset_url": reset_url,
        "domain": "example.com",
        "site_name": "example.com",
    }
    expected_event = NotifyEventType.ACCOUNT_STAFF_RESET_PASSWORD
    mocked_notify.assert_called_once_with(expected_event, payload=expected_payload)
