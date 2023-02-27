import django_filters
import graphene

from ...document.models import Document
from ..core.filters import EnumFilter, ObjectTypeFilter, search_filter
from ..core.types import DateRangeInput, FilterInputObjectType
from ..entry.enums import EntryTypeEnum
from ..utils.filters import filter_range_field


def filter_owner(queryset, name, value):
    if value[0] == "entry":
        return queryset.filter(provider=None)
    if value[0] == "provider":
        return queryset.filter(entry=None)
    return queryset


def filter_expiration_date_range(qs, _, value):
    return filter_range_field(qs, "default_file__expiration_date", value)


def filter_begin_date_range(qs, _, value):
    return filter_range_field(qs, "default_file__begin_date", value)


def filter_entry_type(qs, _, value):
    if not value:
        return qs
    return qs.filter(entry__type=value)


class DocumentFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method=search_filter)
    type = EnumFilter(input_class=EntryTypeEnum, method=filter_entry_type)
    expiration_date = ObjectTypeFilter(
        input_class=DateRangeInput, method=filter_expiration_date_range
    )
    begin_date = ObjectTypeFilter(
        input_class=DateRangeInput, method=filter_begin_date_range
    )

    class Meta:
        model = Document
        fields = ["is_published", "expires", "expiration_date", "begin_date"]


class DocumentFilterInput(FilterInputObjectType):
    class Meta:
        filterset_class = DocumentFilter
