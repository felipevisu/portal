import django_filters
import graphene
from django.db.models import Q

from ...attribute import AttributeInputType, AttributeType
from ...attribute.models import Attribute, AttributeValue
from ..core.filters import (
    EnumFilter,
    GlobalIDMultipleChoiceFilter,
    ListObjectTypeFilter,
)
from ..core.types.common import NonNullList
from ..core.types.filter_input import FilterInputObjectType
from ..utils.filters import filter_by_string_field
from .enums import AttributeInputTypeEnum, AttributeTypeEnum


def filter_attribute_search(qs, _, value):
    if not value:
        return qs
    return qs.filter(Q(slug__ilike=value) | Q(name__ilike=value))


def filter_by_attribute_type(qs, _, value):
    if not value:
        return qs
    values = [value]
    if value in [AttributeType.VEHICLE, AttributeType.PROVIDER]:
        values.append(AttributeType.VEHICLE_AND_PROVIDER)
    return qs.filter(type__in=values)


def filter_slug_list(qs, _, values):
    return qs.filter(slug__in=values)


class AttributeFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method=filter_attribute_search)
    ids = GlobalIDMultipleChoiceFilter(field_name="id")
    type = EnumFilter(input_class=AttributeTypeEnum, method=filter_by_attribute_type)
    slugs = ListObjectTypeFilter(input_class=graphene.String, method=filter_slug_list)

    class Meta:
        model = Attribute
        fields = [
            "value_required",
            "visible_in_website",
            "filterable_in_website",
            "filterable_in_dashboard",
        ]


class AttributeFilterInput(FilterInputObjectType):
    class Meta:
        filterset_class = AttributeFilter


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


class AttributeInputTypeEnumFilterInput(graphene.InputObjectType):
    eq = AttributeInputTypeEnum(required=False)
    one_of = NonNullList(AttributeInputTypeEnum, required=False)


class AttributeTypeEnumFilterInput(graphene.InputObjectType):
    eq = AttributeTypeEnum(required=False)
    one_of = NonNullList(AttributeTypeEnum, required=False)


def filter_attribute_name(qs, _, value):
    return filter_by_string_field(qs, "name", value)


def filter_attribute_slug(qs, _, value):
    return filter_by_string_field(qs, "slug", value)


def filter_with_choices(qs, _, value):
    lookup = Q(input_type__in=AttributeInputType.TYPES_WITH_CHOICES)
    if value is True:
        return qs.filter(lookup)
    elif value is False:
        return qs.exclude(lookup)
    return qs


def filter_attribute_input_type(qs, _, value):
    return filter_by_string_field(qs, "input_type", value)


def filter_attribute_type(qs, _, value):
    return filter_by_string_field(qs, "type", value)
