from ...document import models
from ..core.utils import from_global_id_or_error


def resolve_documents(info):
    user = info.context.user
    return models.Document.published.visible_to_user(user)


def resolve_document(_, global_document_id=None):
    _, document_pk = from_global_id_or_error(global_document_id)
    return models.Document.objects.filter(pk=document_pk).first()
