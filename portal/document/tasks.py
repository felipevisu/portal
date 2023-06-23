import logging

from django.core.exceptions import ObjectDoesNotExist

from portal.document import DocumentLoadStatus

from ..celeryconf import app
from ..plugins.manager import get_plugins_manager
from .events import event_document_loaded_fail, event_document_loaded_from_api
from .models import Document, DocumentLoad


@app.task
def load_new_document_task(document_id, document_load_id, user_id):
    try:
        document = Document.objects.get(id=document_id)
        document_load = DocumentLoad.objects.get(id=document_load_id)
    except ObjectDoesNotExist:
        logging.warning(f"Cannot find document with id: {document_id}.")

    manager = get_plugins_manager()

    try:
        document_file = manager.consult(document)
        if document_file:
            document_load.status = DocumentLoadStatus.SUCCESS
            document_load.document_file = document_file
            event_document_loaded_from_api(
                document_id=document.id,
                document_file_id=document_file.id,
                user_id=user_id,
            )
            document_load.save()
        else:
            raise Exception("A consulta não retornou nenhum documento.")

    except Exception as e:
        error_message = str(e or e.message)
        document_load.status = DocumentLoadStatus.ERROR
        document_load.error_message = error_message
        document_load.save()
        event_document_loaded_fail(
            document_id, error_message=error_message, user_id=user_id
        )


def load_new_document_from_api(document_id, user_id=None, delay=True) -> DocumentLoad:
    document_load = DocumentLoad.objects.create(document_id=document_id)
    loader = load_new_document_task.delay if delay else load_new_document_task
    loader(document_id, document_load.id, user_id)
    document_load.refresh_from_db()
    return document_load
