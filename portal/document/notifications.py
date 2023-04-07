from graphql_relay import to_global_id

from portal.account.models import User

from ..core.notify_events import NotifyEventType
from ..core.utils.notification import get_site_context
from ..event.models import OneTimeToken


def get_document_token(document):
    token = document.tokens.first()
    if not token:
        token = OneTimeToken.objects.create(document=document)
    return str(token.token)


def send_new_document_received(document, manager):
    site_context = get_site_context()
    recipients = User.objects.filter(is_staff=True).values_list("email", flat=True)
    entry_type = "vehicles" if document.entry.type == "vehicle" else "providers"
    payload = {
        "document_id": document.id,
        "document_global_id": to_global_id("Document", document.id),
        "document_name": document.name,
        "token": get_document_token(document),
        "entry_name": document.entry.name,
        "recipient_email": list(recipients),
        "entry_type": entry_type,
        "site_url": site_context.get("site_name"),
        **get_site_context(),
    }
    manager.notify(NotifyEventType.DOCUMENT_RECEIVED, payload)


def send_request_new_document(document, manager, user=None):
    site_context = get_site_context()
    payload = {
        "document_id": document.id,
        "document_global_id": to_global_id("Document", document.id),
        "user_id": user.id if user else None,
        "document_name": document.name,
        "token": get_document_token(document),
        "entry_name": document.entry.name,
        "recipient_email": document.entry.email,
        "site_url": site_context.get("site_name"),
        **get_site_context(),
    }
    manager.notify(NotifyEventType.REQUEST_NEW_DOCUMENT, payload)


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
