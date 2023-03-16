import django_filters
from django.db.models import Q

from ...attribute.models import AttributeValue
from ..core.filters import GlobalIDMultipleChoiceFilter
from ..core.types.filter_input import FilterInputObjectType


class AttributeValueFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")
    ids = GlobalIDMultipleChoiceFilter(field_name="id")

    class Meta:
        model = AttributeValue
        fields = ["search"]

    @classmethod
    def filter_search(cls, queryset, _name, value):
        if not value:
            return queryset
        name_slug_qs = Q(name__ilike=value) | Q(slug__ilike=value)

        return queryset.filter(name_slug_qs)


class AttributeValueFilterInput(FilterInputObjectType):
    class Meta:
        filterset_class = AttributeValueFilter
