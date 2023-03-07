import logging
from dataclasses import asdict
from typing import Union

from django.core.exceptions import ValidationError

from ...core.notify_events import NotifyEventType
from ..base_plugin import BasePlugin, ConfigurationTypeField
from ..models import PluginConfiguration
from . import SendgridConfiguration
from .tasks import (
    send_document_updated_confirmation_to_staff_task,
    send_email_with_dynamic_template_id,
    send_request_new_document_from_provider_task,
)

logger = logging.getLogger(__name__)


EVENT_MAP = {
    NotifyEventType.REQUEST_NEW_DOCUMENT_FROM_PROVIDER: (
        send_request_new_document_from_provider_task,
        "request_new_document_from_provider_template_id",
    ),
    NotifyEventType.DOCUMENT_UPDATED_BY_PROVIDER: (
        send_document_updated_confirmation_to_staff_task,
        "document_updated_confirmation_to_staff_template_id",
    ),
}

HELP_TEXT_TEMPLATE = "ID of the dynamic template in Sendgrid"


class SendgridEmailPlugin(BasePlugin):
    PLUGIN_ID = "portal.notifications.sendgrid_email"
    PLUGIN_NAME = "Sendgrid"
    DEFAULT_ACTIVE = True
    CONFIGURATION_PER_CHANNEL = False

    DEFAULT_CONFIGURATION = [
        {"name": "sender_name", "value": ""},
        {"name": "sender_address", "value": ""},
        {"name": "request_new_document_from_provider_template_id", "value": None},
        {"name": "document_updated_confirmation_to_staff_template_id", "value": None},
        {"name": "api_key", "value": None},
    ]
    CONFIG_STRUCTURE = {
        "sender_name": {
            "type": ConfigurationTypeField.STRING,
            "help_text": "Name which will be visible as 'from' name.",
            "label": "Sender name",
        },
        "sender_address": {
            "type": ConfigurationTypeField.STRING,
            "help_text": "Sender email which will be visible as 'from' email.",
            "label": "Sender email",
        },
        "request_new_document_from_provider_template_id": {
            "type": ConfigurationTypeField.STRING,
            "help_text": HELP_TEXT_TEMPLATE,
            "label": "Request new document email template",
        },
        "document_updated_confirmation_to_staff_template_id": {
            "type": ConfigurationTypeField.STRING,
            "help_text": HELP_TEXT_TEMPLATE,
            "label": "Document updated email template",
        },
        "api_key": {
            "type": ConfigurationTypeField.SECRET,
            "help_text": "Your Sendgrid API key.",
            "label": "API key",
        },
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Convert to dict to easier take config elements
        configuration = {item["name"]: item["value"] for item in self.configuration}
        self.config = SendgridConfiguration(**configuration)

    def notify(self, event: Union[NotifyEventType, str], payload: dict, previous_value):
        if not self.active:
            return previous_value

        event_in_notify_event = event in NotifyEventType.CHOICES

        if not event_in_notify_event:
            logger.info(f"Send email with event {event} as dynamic template ID.")
            send_email_with_dynamic_template_id.delay(
                payload, event, asdict(self.config)
            )
            return previous_value

        if event not in EVENT_MAP:
            logger.warning(f"Missing handler for event {event}")
            return previous_value

        configuration = {item["name"]: item["value"] for item in self.configuration}

        event_task, event_template = EVENT_MAP.get(event)  # type: ignore
        template_id = configuration.get(event_template)
        if not template_id:
            # the empty fields means that we should not send an email for this event.
            return previous_value

        event_task.delay(payload, asdict(self.config))

    @classmethod
    def validate_plugin_configuration(
        cls, plugin_configuration: "PluginConfiguration", **kwargs
    ):
        """Validate if provided configuration is correct."""
        if not plugin_configuration.active:
            return

        configuration = plugin_configuration.configuration
        configuration = {item["name"]: item["value"] for item in configuration}
        api_key = configuration.get("api_key")
        if not api_key:
            error_msg = "Missing SendGrid API Key"
            raise ValidationError(
                {
                    "api_key": ValidationError(error_msg),
                }
            )
