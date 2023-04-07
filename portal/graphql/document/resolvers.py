from ...document import models
from ..core.utils import from_global_id_or_error


def resolve_documents(info):
    user = info.context.user
    return models.Document.objects.filter(entry_id__isnull=False).visible_to_user(user)


def resolve_document(info, global_document_id=None):
    _, document_pk = from_global_id_or_error(global_document_id)
    user = info.context.user
    return (
        models.Document.objects.filter(pk=document_pk, entry_id__isnull=False)
        .visible_to_user(user)
        .first()
    )


def resolve_document_load(info, global_document_load_id=None):
    _, document_load_pk = from_global_id_or_error(global_document_load_id)
    return models.DocumentLoad.objects.filter(pk=document_load_pk).first()
