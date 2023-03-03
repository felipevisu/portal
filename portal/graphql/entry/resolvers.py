from ...entry import models
from ..core.utils import from_global_id_or_error


def resolve_category(_, global_category_id=None, slug=None):
    if global_category_id:
        _, category_pk = from_global_id_or_error(global_category_id)
        category = models.Category.objects.filter(pk=category_pk).first()
    else:
        category = models.Category.objects.filter(slug=slug).first()
    return category


def resolve_categories():
    return models.Category.objects.all()


def resolve_entry(info, global_entry_id=None, slug=None):
    user = info.context.user
    if global_entry_id:
        _, entry_pk = from_global_id_or_error(global_entry_id)
        entry = models.Entry.objects.visible_to_user(user).filter(pk=entry_pk).first()
    else:
        entry = models.Entry.objects.visible_to_user(user).filter(slug=slug).first()
    return entry


def resolve_entries(info):
    user = info.context.user
    return models.Entry.objects.visible_to_user(user)
