from ...attribute import models
from ..core.utils import from_global_id_or_error


def resolve_attributes(info, qs=None):
    qs = qs or models.Attribute.objects.get_visible_to_user(info.context.user)
    return qs


def resolve_attribute(info, global_attribute_id=None, slug=None):
    if info.context.user:
        attributes = models.Attribute.objects.all()
    else:
        attributes = models.Attribute.objects.get_public_attributes()
    if global_attribute_id:
        _, attribute_pk = from_global_id_or_error(global_attribute_id)
        attribute = attributes.filter(pk=attribute_pk).first()
    else:
        attribute = attributes.filter(slug=slug).first()
    return attribute
