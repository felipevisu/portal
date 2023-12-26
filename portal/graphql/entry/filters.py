from collections import defaultdict
from typing import Dict, List, Optional, TypedDict

import django_filters
from django.db.models import Exists, OuterRef, Q

from portal.graphql.channel.filters import get_channel_slug_from_filter_data

from ...attribute import AttributeInputType
from ...attribute.models import AssignedEntryAttributeValue, Attribute, AttributeValue
from ...channel.models import Channel
from ...entry.models import Category, CategoryEntry, Entry, EntryChannelListing
from ..core.filters import (
    EnumFilter,
    GlobalIDMultipleChoiceFilter,
    ListObjectTypeFilter,
    search_filter,
)
from ..core.types import FilterInputObjectType
from ..core.types.filter_input import ChannelFilterInputObjectType
from ..utils import resolve_global_ids_to_primary_keys
from .enums import EntryTypeEnum
from .types import entry_types


def filter_entry_type(qs, _, value):
    if not value:
        return qs
    return qs.filter(type=value)


def filter_entry_types(qs, _, value):
    if not value:
        return qs
    _, entry_type_pks = resolve_global_ids_to_primary_keys(value, entry_types.EntryType)
    return qs.filter(entry_type_id__in=entry_type_pks)


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


def _filter_entries_is_published(qs, _, value, channel_slug):
    channel = Channel.objects.filter(slug=channel_slug).values("pk")
    entry_channel_listings = EntryChannelListing.objects.filter(
        Exists(channel.filter(pk=OuterRef("channel_id"))), is_published=value
    ).values("entry_id")

    return qs.filter(
        Exists(entry_channel_listings.filter(entry_id=OuterRef("pk"))),
    )


def filter_entries_by_attributes_values(qs, queries):
    filters = []
    for values in queries.values():
        assigned_entry_attribute_values = AssignedEntryAttributeValue.objects.filter(
            value_id__in=values
        )
        entry_attribute_filter = Q(
            Exists(assigned_entry_attribute_values.filter(entry_id=OuterRef("pk")))
        )
        filters.append(entry_attribute_filter)

    return qs.filter(*filters)


class KeyValueDict(TypedDict):
    pk: int
    values: Dict[Optional[bool], int]


def _clean_entry_attributes_boolean_filter_input(filter_value, queries):
    attribute_slugs = [slug for slug, _ in filter_value]
    attributes = Attribute.objects.filter(
        input_type=AttributeInputType.BOOLEAN, slug__in=attribute_slugs
    ).prefetch_related("values")
    values_map: Dict[str, KeyValueDict] = {
        attr.slug: {
            "pk": attr.pk,
            "values": {val.boolean: val.pk for val in attr.values.all()},
        }
        for attr in attributes
    }

    for attr_slug, val in filter_value:
        attr_pk = values_map[attr_slug]["pk"]
        value_pk = values_map[attr_slug]["values"].get(val)
        if value_pk:
            queries[attr_pk] += [value_pk]


def _clean_entry_attributes_filter_input(filter_value, queries):
    attribute_slugs = []
    value_slugs = []
    for attr_slug, val_slugs in filter_value:
        attribute_slugs.append(attr_slug)
        value_slugs.extend(val_slugs)
    attributes_slug_pk_map: Dict[str, int] = {}
    attributes_pk_slug_map: Dict[int, str] = {}
    values_map: Dict[str, Dict[str, int]] = defaultdict(dict)
    for attr_slug, attr_pk in Attribute.objects.filter(
        slug__in=attribute_slugs
    ).values_list("slug", "id"):
        attributes_slug_pk_map[attr_slug] = attr_pk
        attributes_pk_slug_map[attr_pk] = attr_slug

    for (
        attr_pk,
        value_pk,
        value_slug,
    ) in AttributeValue.objects.filter(
        slug__in=value_slugs, attribute_id__in=attributes_pk_slug_map.keys()
    ).values_list("attribute_id", "pk", "slug"):
        attr_slug = attributes_pk_slug_map[attr_pk]
        values_map[attr_slug][value_slug] = value_pk

    # Convert attribute:value pairs into a dictionary where
    # attributes are keys and values are grouped in lists
    for attr_name, val_slugs in filter_value:
        if attr_name not in attributes_slug_pk_map:
            raise ValueError("Unknown attribute name: %r" % (attr_name,))
        attr_pk = attributes_slug_pk_map[attr_name]
        attr_val_pk = [
            values_map[attr_name][val_slug]
            for val_slug in val_slugs
            if val_slug in values_map[attr_name]
        ]
        queries[attr_pk] += attr_val_pk


def filter_entries_by_attributes(
    qs,
    filter_values,
    filter_boolean_values,
):
    queries: Dict[int, List[int]] = defaultdict(list)
    try:
        if filter_values:
            _clean_entry_attributes_filter_input(filter_values, queries)
        if filter_boolean_values:
            _clean_entry_attributes_boolean_filter_input(filter_boolean_values, queries)
    except ValueError:
        return Entry.objects.none()
    return filter_entries_by_attributes_values(qs, queries)


def _filter_attributes(qs, _, value):
    if value:
        value_list = []
        boolean_list = []
        for v in value:
            slug = v["slug"]
            if "values" in v:
                value_list.append((slug, v["values"]))
            elif "boolean" in v:
                boolean_list.append((slug, v["boolean"]))

        qs = filter_entries_by_attributes(
            qs,
            value_list,
            boolean_list,
        )
    return qs


class CategoryFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method=search_filter)
    type = EnumFilter(input_class=EntryTypeEnum, method=filter_entry_type)
    ids = GlobalIDMultipleChoiceFilter(field_name="id")

    class Meta:
        model = Category
        fields = ["search"]


class EntryFilter(django_filters.FilterSet):
    is_published = django_filters.BooleanFilter(method="filter_is_published")
    search = django_filters.CharFilter(method=search_filter)
    categories = GlobalIDMultipleChoiceFilter(method=filter_categories)
    type = EnumFilter(input_class=EntryTypeEnum, method=filter_entry_type)
    entry_types = GlobalIDMultipleChoiceFilter(method=filter_entry_types)
    attributes = ListObjectTypeFilter(
        input_class="portal.graphql.attribute.types.AttributeInput",
        method="filter_attributes",
    )

    class Meta:
        model = Entry
        fields = ["is_published", "attributes"]

    def filter_is_published(self, queryset, name, value):
        channel_slug = get_channel_slug_from_filter_data(self.data)
        return _filter_entries_is_published(
            queryset,
            name,
            value,
            channel_slug,
        )

    def filter_attributes(self, queryset, name, value):
        return _filter_attributes(queryset, name, value)


class CategoryFilterInput(FilterInputObjectType):
    class Meta:
        filterset_class = CategoryFilter


class EntryFilterInput(ChannelFilterInputObjectType):
    class Meta:
        filterset_class = EntryFilter
