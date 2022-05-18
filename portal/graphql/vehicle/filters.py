import django_filters

from ...vehicle.models import Category, Vehicle
from ..core.filters import search_filter


class CategoryFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method=search_filter)

    class Meta:
        model = Category
        fields = ['search']


class VehicleFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method=search_filter)

    class Meta:
        model = Vehicle
        fields = {
            'is_published': ['exact'],
        }
