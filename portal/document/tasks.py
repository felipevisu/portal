import logging

from django.core.exceptions import ObjectDoesNotExist

from portal.document import DocumentLoadStatus

from ..celeryconf import app
from ..plugins.manager import get_plugins_manager
from .events import event_document_loaded_fail, event_document_loaded_from_api
from .models import Document, DocumentLoad


@app.task
def load_new_document_from_api_task(document_id, document_load_id, user_id):
    try:
        document = Document.objects.get(id=document_id)
        document_load = DocumentLoad.objects.get(id=document_load_id)
    except ObjectDoesNotExist:
        logging.warning(f"Cannot find document with id: {document_id}.")

    manager = get_plugins_manager()

    try:
        document_file = manager.consult(document)
        document_load.status = DocumentLoadStatus.SUCCESS
        document_load.document_file = document_file
        document_load.save()
        event_document_loaded_from_api(
            document_id=document.id, document_file_id=document_file.id, user_id=user_id
        )
    except Exception as e:
        error_message = str(e.message)
        document_load.status = DocumentLoadStatus.ERROR
        document_load.error_message = error_message
        document_load.save()
        event_document_loaded_fail(document_id, error_message, user_id=user_id)


def load_new_document_from_api(document_id, user_id=None):
    document_load = DocumentLoad.objects.create(document_id=document_id)
    load_new_document_from_api_task.delay(document_id, document_load.id, user_id)
    return document_load
