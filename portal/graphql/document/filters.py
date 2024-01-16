import django_filters

from ...document import DocumentFileStatus
from ...document.models import Document
from ..core.filters import EnumFilter, ObjectTypeFilter, search_filter
from ..core.types import DateRangeInput, FilterInputObjectType
from ..utils.filters import filter_range_field


def filter_expiration_date_range(qs, _, value):
    return filter_range_field(qs, "default_file__expiration_date", value)


def filter_begin_date_range(qs, _, value):
    return filter_range_field(qs, "default_file__begin_date", value)


def waiting_filter(queryset, _, value):
    if value:
        return queryset.filter(files__status=DocumentFileStatus.WAITING)
    return queryset.exclude(files__status=DocumentFileStatus.WAITING)


class DocumentFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method=search_filter)
    expiration_date = ObjectTypeFilter(
        input_class=DateRangeInput, method=filter_expiration_date_range
    )
    begin_date = ObjectTypeFilter(
        input_class=DateRangeInput, method=filter_begin_date_range
    )
    waiting = django_filters.BooleanFilter(method=waiting_filter)

    class Meta:
        model = Document
        fields = ["is_published", "expires", "expiration_date", "begin_date"]


class DocumentFilterInput(FilterInputObjectType):
    class Meta:
        filterset_class = DocumentFilter
