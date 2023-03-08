from unittest import mock

import pytest

from ....account.notifications import get_default_user_payload
from ..notify_events import send_set_staff_password_email, send_staff_reset_password

pytestmark = pytest.mark.django_db


@mock.patch(
    "portal.plugins.admin_email.notify_events.send_staff_password_reset_email_task."
    "delay"
)
def test_send_account_password_reset_event(
    mocked_email_task, staff_user, admin_email_plugin
):
    token = "token123"
    payload = {
        "user": get_default_user_payload(staff_user),
        "recipient_email": "user@example.com",
        "token": token,
        "reset_url": f"http://localhost:8000/redirect{token}",
        "domain": "localhost:8000",
        "site_name": "portal",
    }
    config = {"host": "localhost", "port": "1025"}
    send_staff_reset_password(
        payload=payload, config=config, plugin=admin_email_plugin()
    )
    mocked_email_task.assert_called_with(
        payload["recipient_email"], payload, config, mock.ANY, mock.ANY
    )


@mock.patch(
    "portal.plugins.admin_email.notify_events.send_staff_password_reset_email_task."
    "delay"
)
def test_send_account_password_reset_event_empty_template(
    mocked_email_task, staff_user, admin_email_plugin
):
    token = "token123"
    payload = {
        "user": get_default_user_payload(staff_user),
        "recipient_email": "user@example.com",
        "token": token,
        "reset_url": f"http://localhost:8000/redirect{token}",
        "domain": "localhost:8000",
        "site_name": "portal",
    }
    config = {"host": "localhost", "port": "1025"}
    send_staff_reset_password(
        payload=payload,
        config=config,
        plugin=admin_email_plugin(staff_password_reset_template=""),
    )
    assert not mocked_email_task.called


@mock.patch(
    "portal.plugins.admin_email.notify_events.send_set_staff_password_email_task.delay"
)
def test_send_set_staff_password_email(mocked_email_task, admin_email_plugin):
    payload = {
        "recipient_email": "admin@example.com",
        "redirect_url": "http://127.0.0.1:8000/redirect",
        "token": "token123",
    }
    config = {"host": "localhost", "port": "1025"}
    send_set_staff_password_email(
        payload=payload, config=config, plugin=admin_email_plugin()
    )
    mocked_email_task.assert_called_with(
        payload["recipient_email"], payload, config, mock.ANY, mock.ANY
    )


@mock.patch(
    "portal.plugins.admin_email.notify_events.send_set_staff_password_email_task.delay"
)
def test_send_set_staff_password_email_empty_template(
    mocked_email_task, admin_email_plugin
):
    payload = {
        "recipient_email": "admin@example.com",
        "redirect_url": "http://127.0.0.1:8000/redirect",
        "token": "token123",
    }
    config = {"host": "localhost", "port": "1025"}
    send_set_staff_password_email(
        payload=payload,
        config=config,
        plugin=admin_email_plugin(set_staff_password_template=""),
    )
    assert not mocked_email_task.called
