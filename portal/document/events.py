from ..account.models import User
from ..document.models import Document
from ..event import EventTypes
from ..event.models import Event


def build_params(document_id, user_id):
    document = Document.objects.filter(id=document_id).first()
    user = User.objects.filter(id=None).first()
    params = {"document_id": document_id, "user_id": user_id}
    if document:
        params["document_name"] = document.entry.name + " / " + document.name
    if user:
        params["user_email"] = user.email
    return params


def event_document_created(document_id, user_id=None):
    Event.objects.create(
        type=EventTypes.DOCUMENT_CREATED, **build_params(document_id, user_id)
    )


def event_document_deleted(document_id, user_id=None):
    Event.objects.create(
        type=EventTypes.DOCUMENT_DELETED,
        **build_params(document_id, user_id),
    )


def event_document_received(document_id, user_id=None):
    return Event.objects.create(
        type=EventTypes.DOCUMENT_RECEIVED, **build_params(document_id, user_id)
    )


def event_document_approved(document_id, user_id=None):
    return Event.objects.create(
        type=EventTypes.DOCUMENT_APPROVED, **build_params(document_id, user_id)
    )


def event_document_declined(document_id, user_id=None):
    return Event.objects.create(
        type=EventTypes.DOCUMENT_DECLINED, **build_params(document_id, user_id)
    )


def event_document_requested(document_id, user_id=None):
    return Event.objects.create(
        type=EventTypes.DOCUMENT_REQUESTED, **build_params(document_id, user_id)
    )


def event_document_loaded_from_api(document_id, document_file_id, user_id=None):
    parameters = {"document_file_id": document_file_id}
    return Event.objects.create(
        type=EventTypes.DOCUMENT_LOADED_FROM_API,
        parameters=parameters,
        **build_params(document_id, user_id),
    )


def event_document_loaded_fail(document_id, user_id=None, error_message=""):
    return Event.objects.create(
        type=EventTypes.DOCUMENT_LOADED_FAIL,
        message=error_message,
        **build_params(document_id, user_id),
    )
