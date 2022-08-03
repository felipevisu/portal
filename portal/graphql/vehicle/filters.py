import django_filters

from ...vehicle.models import Category, Vehicle
from ..core.filters import GlobalIDMultipleChoiceFilter, search_filter
from ..utils import resolve_global_ids_to_primary_keys
from . import types as vehicle_types


def filter_categories(qs, _, value):
    if value:
        _, category_pks = resolve_global_ids_to_primary_keys(
            value, vehicle_types.Category
        )
        return qs.filter(category_id__in=category_pks)
    return qs


class CategoryFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method=search_filter)

    class Meta:
        model = Category
        fields = ['search']


class VehicleFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method=search_filter)
    categories = GlobalIDMultipleChoiceFilter(method=filter_categories)

    class Meta:
        model = Vehicle
        fields = ['is_published', 'category']
