import logging

from django.core.exceptions import ObjectDoesNotExist

from portal.document import DocumentLoadStatus

from ..celeryconf import app
from ..plugins.manager import get_plugins_manager
from .events import event_document_loaded_from_api
from .models import Document, DocumentLoad


@app.task
def load_new_document_from_api_task(document_id, load_id):
    try:
        document = Document.objects.get(id=document_id)
        document_load = DocumentLoad.objects.get(id=load_id)
    except ObjectDoesNotExist:
        logging.warning(f"Cannot find document with id: {document_id}.")

    manager = get_plugins_manager()

    try:
        document_file = manager.consult(document)
        document_load.status = DocumentLoadStatus.SUCCESS
        document_load.document_file = document_file
        document_load.save()
        event_document_loaded_from_api(
            document_id=document.id, document_file_id=document_file.id
        )
    except Exception as e:
        document_load.status = DocumentLoadStatus.ERROR
        document_load.error_message = str(e.message)
        document_load.save()


def load_new_document_from_api(document_id):
    document_load = DocumentLoad.objects.create(document_id=document_id)
    load_new_document_from_api_task.delay(document_id, document_load.id)
    return document_load
