from ..core.notify_events import NotifyEventType
from ..core.utils.notification import get_site_context
from .utils import build_request_new_document_payload


def send_new_document_received(document, manager):
    payload = {
        "document": document.id,
        "recipient_email": None,  # indentify the user requestor
        **get_site_context(),
    }
    manager.notify(NotifyEventType.DOCUMENT_RECEIVED, payload)


def send_new_document_approved(document, manager, user):
    payload = {
        "document": document.id,
        "recipient_email": user.email,
        "user_id": user.id,
        **get_site_context(),
    }
    manager.notify(NotifyEventType.DOCUMENT_APPROVED, payload)


def send_new_document_declined(document, manager, user):
    payload = {
        "document": document.id,
        "recipient_email": user.email,
        "user_id": user.id,
        **get_site_context(),
    }
    manager.notify(NotifyEventType.DOCUMENT_DECLINED, payload)


def send_request_new_document(document, manager, user=None):
    payload = build_request_new_document_payload(document, user)
    manager.notify(NotifyEventType.REQUEST_NEW_DOCUMENT, payload)
