from . import EventTypes
from .models import Event


def event_document_received(document_id):
    return Event.objects.create(
        document_id=document_id, type=EventTypes.DOCUMENT_RECEIVED
    )


def event_document_approved(document_id, user_id):
    return Event.objects.create(
        document_id=document_id, user_id=user_id, type=EventTypes.DOCUMENT_APPROVED
    )


def event_document_declined(document_id, user_id):
    return Event.objects.create(
        document_id=document_id, user_id=user_id, type=EventTypes.DOCUMENT_DECLINED
    )


def event_document_requested(document_id, user_id=None):
    return Event.objects.create(
        document_id=document_id,
        user_id=user_id,
        type=EventTypes.DOCUMENT_REQUESTED,
    )
