import logging

from python_http_client import exceptions
from sendgrid import SendGridAPIClient, SendGridException
from sendgrid.helpers.mail import Mail

from ...celeryconf import app
from ...event import events
from ...graphql.core.utils import from_global_id_or_none
from . import SendgridConfiguration

logger = logging.getLogger(__name__)

CELERY_RETRY_BACKOFF = 60
CELERY_RETRY_MAX = 5


def send_email(configuration: SendgridConfiguration, template_id, payload):
    recipient_email = payload["recipient_email"]
    sendgrid_client = SendGridAPIClient(configuration.api_key)
    from_email = (configuration.sender_address, configuration.sender_name)
    message = Mail(from_email=from_email, to_emails=recipient_email)
    message.template_id = template_id
    try:
        sendgrid_client.send(message)
    except exceptions.BadRequestsError as e:
        logger.warning("Bad request to Sendgrid, response: %s" % e.body)


@app.task(
    autoretry_for=(SendGridException,),
    retry_backoff=CELERY_RETRY_BACKOFF,
    retry_kwargs={"max_retries": CELERY_RETRY_MAX},
    compression="zlib",
)
def send_document_updated_confirmation_to_staff_task(
    payload: dict, configuration: dict
):
    configuration = SendgridConfiguration(**configuration)
    document_id = payload.get("document", {}).get("id")
    document_id = from_global_id_or_none(document_id)
    send_email(
        configuration=configuration,
        template_id=configuration.document_updated_confirmation_to_staff_template_id,
        payload=payload,
    )
    events.event_document_updated_by_provider(document_id=document_id)


@app.task(
    autoretry_for=(SendGridException,),
    retry_backoff=CELERY_RETRY_BACKOFF,
    retry_kwargs={"max_retries": CELERY_RETRY_MAX},
    compression="zlib",
)
def send_request_new_document_from_provider_task(payload: dict, configuration: dict):
    configuration = SendgridConfiguration(**configuration)
    document_id = payload.get("document", {})
    send_email(
        configuration=configuration,
        template_id=configuration.request_new_document_from_provider_template_id,
        payload=payload,
    )
    events.event_provider_notified_about_expired_document(document_id=document_id)


@app.task(
    autoretry_for=(SendGridException,),
    retry_backoff=CELERY_RETRY_BACKOFF,
    retry_kwargs={"max_retries": CELERY_RETRY_MAX},
    compression="zlib",
)
def send_email_with_dynamic_template_id(
    payload: dict, template_id: str, configuration: dict
):
    configuration = SendgridConfiguration(**configuration)
    send_email(
        configuration=configuration,
        template_id=template_id,
        payload=payload,
    )
