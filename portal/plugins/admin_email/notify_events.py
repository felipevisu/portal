from typing import TYPE_CHECKING

from ..email_common import get_email_subject, get_email_template_or_default
from . import constants
from .tasks import (
    send_set_staff_password_email_task,
    send_staff_password_reset_email_task,
)

if TYPE_CHECKING:
    from .plugin import AdminEmailPlugin


def send_set_staff_password_email(
    payload: dict, config: dict, plugin: "AdminEmailPlugin"
):
    recipient_email = payload["recipient_email"]
    template = get_email_template_or_default(
        plugin,
        constants.SET_STAFF_PASSWORD_TEMPLATE_FIELD,
        constants.SET_STAFF_PASSWORD_DEFAULT_TEMPLATE,
        constants.DEFAULT_EMAIL_TEMPLATES_PATH,
    )
    if not template:
        # Empty template means that we don't want to trigger a given event.
        return
    subject = get_email_subject(
        plugin.configuration,
        constants.SET_STAFF_PASSWORD_SUBJECT_FIELD,
        constants.SET_STAFF_PASSWORD_DEFAULT_SUBJECT,
    )
    send_set_staff_password_email_task.delay(
        recipient_email, payload, config, subject, template
    )


def send_staff_reset_password(payload: dict, config: dict, plugin: "AdminEmailPlugin"):
    recipient_email = payload.get("recipient_email")
    if recipient_email:
        template = get_email_template_or_default(
            plugin,
            constants.STAFF_PASSWORD_RESET_TEMPLATE_FIELD,
            constants.STAFF_PASSWORD_RESET_DEFAULT_TEMPLATE,
            constants.DEFAULT_EMAIL_TEMPLATES_PATH,
        )
        if not template:
            # Empty template means that we don't want to trigger a given event.
            return
        subject = get_email_subject(
            plugin.configuration,
            constants.STAFF_PASSWORD_RESET_SUBJECT_FIELD,
            constants.STAFF_PASSWORD_RESET_DEFAULT_SUBJECT,
        )
        send_staff_password_reset_email_task.delay(
            recipient_email, payload, config, subject, template
        )
