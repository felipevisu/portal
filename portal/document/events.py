from ..event import EventTypes
from ..event.models import Event


def event_document_created(document_id, user):
    Event.objects.create(
        type=EventTypes.DOCUMENT_CREATED, document_id=document_id, user=user
    )


def event_document_updated(document_id, user):
    Event.objects.create(
        type=EventTypes.DOCUMENT_UPDATED, document_id=document_id, user=user
    )


def event_document_deleted(document, user):
    parameters = {"name": document.name, "entry": document.entry.name}
    Event.objects.create(
        type=EventTypes.DOCUMENT_DELETED, parameters=parameters, user=user
    )


def event_document_received(document_id):
    return Event.objects.create(
        type=EventTypes.DOCUMENT_RECEIVED, document_id=document_id
    )


def event_document_approved(document_id, user_id):
    return Event.objects.create(
        type=EventTypes.DOCUMENT_APPROVED, document_id=document_id, user_id=user_id
    )


def event_document_declined(document_id, user_id):
    return Event.objects.create(
        type=EventTypes.DOCUMENT_DECLINED, document_id=document_id, user_id=user_id
    )


def event_document_requested(document_id, user_id=None):
    return Event.objects.create(
        type=EventTypes.DOCUMENT_REQUESTED, document_id=document_id, user_id=user_id
    )


def event_document_loaded_from_api(document_id, document_file_id):
    parameters = {"document_file_id": document_file_id}
    return Event.objects.create(
        type=EventTypes.DOCUMENT_LOADED_FROM_API,
        document_id=document_id,
        parameters=parameters,
    )
