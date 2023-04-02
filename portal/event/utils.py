from graphql_relay import to_global_id

from ..core.utils.notification import get_site_context
from .models import OneTimeToken


def get_document_token(document):
    token = document.tokens.first()
    if not token:
        token = OneTimeToken.objects.create(document=document)
    return str(token.token)


def build_request_new_document_payload(document, user=None):
    site_context = get_site_context()
    payload = {
        "document_id": document.id,
        "user_id": user.id if user else None,
        "document_global_id": to_global_id("Document", document.id),
        "document_name": document.name,
        "token": get_document_token(document),
        "entry_name": document.entry.name,
        "recipient_email": document.entry.email,
        "site_url": site_context.get("site_name"),
        **get_site_context(),
    }
    return payload
