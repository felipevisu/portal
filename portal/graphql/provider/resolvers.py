from ...provider import models
from ..core.utils import from_global_id_or_error


def resolve_segment(_, global_segment_id=None, slug=None):
    if global_segment_id:
        _, segment_pk = from_global_id_or_error(global_segment_id)
        segment = models.Segment.objects.filter(pk=segment_pk).first()
    else:
        segment = models.Segment.objects.filter(slug=slug).first()
    return segment


def resolve_providers(info):
    user = info.context.user
    return models.Provider.published.visible_to_user(user)


def resolve_provider(info, global_provider_id=None, slug=None):
    user = info.context.user
    if global_provider_id:
        _, provider_pk = from_global_id_or_error(global_provider_id)
        provider = models.Provider.published.visible_to_user(
            user).filter(pk=provider_pk).first()
    else:
        provider = models.Provider.published.visible_to_user(
            user).filter(slug=slug).first()
    return provider


def resolve_documents(info):
    user = info.context.user
    return models.Document.published.visible_to_user(user)


def resolve_document(_, global_document_id=None):
    _, document_pk = from_global_id_or_error(global_document_id)
    return models.Document.objects.filter(pk=document_pk).first()
