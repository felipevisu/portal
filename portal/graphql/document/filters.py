
import django_filters
import graphene

from ...document.models import Document
from ..core.filters import ListObjectTypeFilter, ObjectTypeFilter, search_filter
from ..core.types import DateRangeInput, FilterInputObjectType
from ..utils.filters import filter_range_field


def filter_owner(queryset, name, value):
    if value == 'vehicle':
        return queryset.filter(provider=None)
    if value == 'provider':
        return queryset.filter(vehicle=None)
    return queryset


def filter_expiration_date_range(qs, _, value):
    return filter_range_field(qs, "expiration_date", value)


def filter_begin_date_range(qs, _, value):
    return filter_range_field(qs, "begin_date", value)


class OwnerType(graphene.Enum):
    PROVIDER = "provider"
    VEHICLE = "vehicle"


class DocumentFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method=search_filter)
    owner = ListObjectTypeFilter(input_class=OwnerType, method=filter_owner)
    expiration_date = ObjectTypeFilter(input_class=DateRangeInput, method=filter_expiration_date_range)
    begin_date = ObjectTypeFilter(input_class=DateRangeInput, method=filter_begin_date_range)

    class Meta:
        model = Document
        fields = ['is_published', 'expires', 'expiration_date', 'begin_date']


class DocumentFilterInput(FilterInputObjectType):
    class Meta:
        filterset_class = DocumentFilter
