from ..core.notify_events import NotifyEventType
from ..core.utils.notification import get_site_context
from .utils import build_request_new_document_payload


def send_document_updated_confirmation_to_staff(document, user, manager):
    payload = {
        "document": document.id,
        "recipient_email": user.email,
        **get_site_context(),
    }
    manager.notify(NotifyEventType.DOCUMENT_UPDATED_BY_PROVIDER, payload)


def send_request_new_document_from_provider(document, manager):
    payload = build_request_new_document_payload(document)
    manager.notify(NotifyEventType.REQUEST_NEW_DOCUMENT_FROM_PROVIDER, payload)
