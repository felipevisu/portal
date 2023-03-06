from . import EventTypes
from .models import Event


def event_document_updated_by_provider(document_id):
    return Event.objects.create(
        document_id=document_id, type=EventTypes.DOCUMENT_UPDATED_BY_PROVIDER
    )


def event_document_updated_by_staff(document_id, user):
    return Event.objects.create(
        document_id=document_id, user=user, type=EventTypes.DOCUMENT_UPDATED_BY_STAFF
    )


def event_provider_notified_about_expired_document(document_id):
    return Event.objects.create(
        document_id=document_id,
        type=EventTypes.PROVIDER_NOTIFIED_ABOUT_EXPIRED_DOCUMENT,
    )


def event_new_document_requested_by_staff(document_id, user):
    return Event.objects.create(
        document_id=document_id,
        user=user,
        type=EventTypes.NEW_DOCUMENT_REQUESTED_BY_STAFF,
    )
