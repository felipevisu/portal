import django_filters

from ...entry.models import Category, Entry
from ..core.filters import EnumFilter, GlobalIDMultipleChoiceFilter, search_filter
from ..core.types import FilterInputObjectType
from ..utils import resolve_global_ids_to_primary_keys
from . import types as entry_types
from .enums import EntryTypeEnum


def filter_entry_type(qs, _, value):
    if not value:
        return qs
    return qs.filter(type=value)


def filter_categories(qs, _, value):
    if value:
        _, category_pks = resolve_global_ids_to_primary_keys(
            value, entry_types.Category
        )
        return qs.filter(category_id__in=category_pks)
    return qs


class CategoryFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method=search_filter)

    class Meta:
        model = Category
        fields = ["search"]


class EntryFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method=search_filter)
    categories = GlobalIDMultipleChoiceFilter(method=filter_categories)
    type = EnumFilter(input_class=EntryTypeEnum, method=filter_entry_type)

    class Meta:
        model = Entry
        fields = ["is_published", "category"]


class CategoryFilterInput(FilterInputObjectType):
    class Meta:
        filterset_class = CategoryFilter


class EntryFilterInput(FilterInputObjectType):
    class Meta:
        filterset_class = EntryFilter
