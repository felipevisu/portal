import django_filters
from django.db.models import Exists, OuterRef

from ...entry.models import Category, CategoryEntry, Entry
from ..core.filters import EnumFilter, GlobalIDMultipleChoiceFilter, search_filter
from ..core.types import FilterInputObjectType
from ..core.types.filter_input import ChannelFilterInputObjectType
from ..utils import resolve_global_ids_to_primary_keys
from .enums import EntryTypeEnum


def filter_entry_type(qs, _, value):
    if not value:
        return qs
    return qs.filter(type=value)


def filter_entries_by_categories(qs, category_pks):
    category_entries = CategoryEntry.objects.filter(
        category_id__in=category_pks
    ).values("entry_id")
    return qs.filter(Exists(category_entries.filter(entry_id=OuterRef("pk"))))


def filter_categories(qs, _, value):
    if value:
        _, category_pks = resolve_global_ids_to_primary_keys(value)
        qs = filter_entries_by_categories(qs, category_pks)
    return qs


class CategoryFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method=search_filter)
    type = EnumFilter(input_class=EntryTypeEnum, method=filter_entry_type)

    class Meta:
        model = Category
        fields = ["search"]


class EntryFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method=search_filter)
    categories = GlobalIDMultipleChoiceFilter(method=filter_categories)
    type = EnumFilter(input_class=EntryTypeEnum, method=filter_entry_type)

    class Meta:
        model = Entry
        fields = []


class CategoryFilterInput(FilterInputObjectType):
    class Meta:
        filterset_class = CategoryFilter


class EntryFilterInput(ChannelFilterInputObjectType):
    class Meta:
        filterset_class = EntryFilter
