from graphql_relay import to_global_id

from ..account.models import User
from ..core.notify_events import NotifyEventType
from ..core.utils.notification import get_site_context
from .utils import build_request_new_document_payload


def send_new_document_received(document, manager):
    site_context = get_site_context()
    recipients = User.objects.filter(is_staff=True).values_list("email", flat=True)
    entry_type = "vehicles" if document.entry.type == "vehicle" else "providers"
    payload = {
        "document_id": document.id,
        "document_global_id": to_global_id("Document", document.id),
        "entry_global_id": to_global_id("Entry", document.entry.id),
        "entry_type": entry_type,
        "recipient_email": list(recipients),
        "site_url": site_context.get("site_name"),
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
