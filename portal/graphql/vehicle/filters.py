from django_filters import FilterSet

from ...vehicle.models import Category, Vehicle


class CategoryFilter(FilterSet):
    class Meta:
        model = Category
        fields = {
            'name': ['exact', 'icontains', 'istartswith'],
        }


class VehicleFilter(FilterSet):
    class Meta:
        model = Vehicle
        fields = {
            'name': ['exact', 'icontains', 'istartswith'],
            'document_number': ['exact'],
            'is_published': ['exact'],
        }
