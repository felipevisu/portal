from ...vehicle import models
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


def resolve_vehicle(info, global_vehicle_id=None, slug=None):
    user = info.context.user
    if global_vehicle_id:
        _, vehicle_pk = from_global_id_or_error(global_vehicle_id)
        vehicle = models.Vehicle.published.visible_to_user(
            user).filter(pk=vehicle_pk).first()
    else:
        vehicle = models.Vehicle.published.visible_to_user(
            user).filter(slug=slug).first()
    return vehicle


def resolve_vehicles(info):
    user = info.context.user
    return models.Vehicle.published.visible_to_user(user)
