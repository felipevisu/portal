from unittest import mock

import pytest

from ....account.notifications import get_default_user_payload
from ...email_common import DEFAULT_EMAIL_VALUE, EmailConfig
from ...manager import get_plugins_manager
from ..tasks import (
    send_set_staff_password_email_task,
    send_staff_password_reset_email_task,
)

pytestmark = pytest.mark.django_db


def test_plugin_manager_doesnt_load_email_templates_from_db(
    admin_email_plugin, admin_email_template, settings
):
    settings.PLUGINS = ["portal.plugins.admin_email.plugin.AdminEmailPlugin"]
    manager = get_plugins_manager()
    plugin = manager.all_plugins[0]

    email_config_item = None
    for config_item in plugin.configuration:
        if config_item["name"] == admin_email_template.name:
            email_config_item = config_item

    # Assert that accessing plugin configuration directly from manager doesn't load
    # email template from DB but returns default email value.
    assert email_config_item
    assert email_config_item["value"] == DEFAULT_EMAIL_VALUE


@mock.patch("portal.plugins.admin_email.tasks.send_email")
def test_send_staff_password_reset_email_task_custom_template(
    mocked_send_email, email_dict_config, admin_email_plugin, staff_user
):
    expected_template_str = "<html><body>Template body</body></html>"
    expected_subject = "Test Email Subject"
    admin_email_plugin(
        staff_password_reset_template=expected_template_str,
        staff_password_reset_subject=expected_subject,
    )
    token = "token123"
    recipient_email = "admin@example.com"
    payload = {
        "user": get_default_user_payload(staff_user),
        "recipient_email": recipient_email,
        "token": token,
        "reset_url": f"http://localhost:8000/redirect{token}",
        "domain": "localhost:8000",
        "site_name": "portal",
    }

    send_staff_password_reset_email_task(
        recipient_email,
        payload,
        email_dict_config,
        expected_subject,
        expected_template_str,
    )

    email_config = EmailConfig(**email_dict_config)
    mocked_send_email.assert_called_with(
        config=email_config,
        recipient_list=[recipient_email],
        context=payload,
        subject=expected_subject,
        template_str=expected_template_str,
    )


@mock.patch("portal.plugins.email_common.send_mail")
def test_send_set_staff_password_email_task_default_template(
    mocked_send_mail, email_dict_config, staff_user
):
    recipient_email = "user@example.com"
    token = "token123"
    payload = {
        "user": get_default_user_payload(staff_user),
        "recipient_email": recipient_email,
        "token": token,
        "password_set_url": f"http://localhost:8000/redirect{token}",
        "site_name": "Saleor",
        "domain": "localhost:8000",
    }

    send_set_staff_password_email_task(
        recipient_email,
        payload,
        email_dict_config,
        "subject",
        "template",
    )

    # confirm that mail has correct structure and email was sent
    assert mocked_send_mail.called


@mock.patch("portal.plugins.admin_email.tasks.send_email")
def test_send_set_staff_password_email_task_custom_template(
    mocked_send_email, email_dict_config, admin_email_plugin, staff_user
):
    expected_template_str = "<html><body>Template body</body></html>"
    expected_subject = "Test Email Subject"
    admin_email_plugin(
        set_staff_password_template=expected_template_str,
        set_staff_password_title=expected_subject,
    )
    recipient_email = "user@example.com"
    token = "token123"
    payload = {
        "user": get_default_user_payload(staff_user),
        "recipient_email": recipient_email,
        "token": token,
        "password_set_url": f"http://localhost:8000/redirect{token}",
        "site_name": "Saleor",
        "domain": "localhost:8000",
    }

    send_set_staff_password_email_task(
        recipient_email,
        payload,
        email_dict_config,
        expected_subject,
        expected_template_str,
    )

    email_config = EmailConfig(**email_dict_config)
    mocked_send_email.assert_called_with(
        config=email_config,
        recipient_list=[recipient_email],
        context=payload,
        subject=expected_subject,
        template_str=expected_template_str,
    )
