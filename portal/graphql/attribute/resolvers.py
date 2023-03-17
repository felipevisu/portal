from ...attribute import models


def resolve_attributes(info, qs=None):

    qs = qs or models.Attribute.objects.get_visible_to_user(info.context.user)
    return qs
