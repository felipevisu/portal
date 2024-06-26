from urllib.parse import urlencode


from django.contrib.auth.tokens import default_token_generator

from ..graphql.core.utils import to_global_id_or_none

from ..core.notify_events import NotifyEventType
from ..core.url import prepare_url
from ..core.utils.notification import get_site_context
from .models import User


def get_default_user_payload(user: User):
    payload = {
        "id": to_global_id_or_none(user),
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_staff": user.is_staff,
        "is_active": user.is_active,
    }
    return payload


def send_password_reset_notification(user, redirect_url, manager):
    """Trigger sending a password reset notification for the given customer/staff."""
    token = default_token_generator.make_token(user)
    params = urlencode({"email": user.email, "token": token})
    reset_url = prepare_url(params, redirect_url)

    payload = {
        "user": get_default_user_payload(user),
        "recipient_email": user.email,
        "token": token,
        "reset_url": reset_url,
        **get_site_context(),
    }

    event = NotifyEventType.ACCOUNT_STAFF_RESET_PASSWORD
    manager.notify(event, payload=payload)
