from django.db.models import QuerySet

from ..core.types import SortInputObjectType

REVERSED_DIRECTION = {
    "-": "",
    "": "-",
}


def sort_queryset_resolver(qs, kwargs):
    sort_by = kwargs.get("sort_by")
    reversed = True if "last" in kwargs else False
    if sort_by:
        iterable = sort_queryset(
            queryset=qs,
            sort_by=sort_by,
            reversed=reversed
        )
    else:
        iterable = sort_queryset_by_default(
            queryset=qs, reversed=reversed
        )
    return iterable


def sort_queryset(
    queryset: QuerySet,
    sort_by: SortInputObjectType,
    reversed: bool
):
    sorting_direction = str(sort_by.direction)
    if reversed:
        sorting_direction = REVERSED_DIRECTION[sorting_direction]

    sorting_field = sort_by.field
    sort_enum = sort_by._meta.sort_enum
    sorting_fields = sort_enum.get(sorting_field)
    sorting_field_value = sorting_fields.value
    sorting_list = [f"{sorting_direction}{field}" for field in sorting_field_value]

    return queryset.order_by(*sorting_list)


def get_model_default_ordering(model_class):
    default_ordering = []
    model_ordering = model_class._meta.ordering
    for field in model_ordering:
        if isinstance(field, str):
            default_ordering.append(field)
        else:
            direction = "-" if field.descending else ""
            default_ordering.append(f"{direction}{field.expression.name}")
    return default_ordering


def sort_queryset_by_default(queryset: QuerySet, reversed: bool):
    queryset_model = queryset.model
    default_ordering = ["pk"]
    if queryset_model and queryset_model._meta.ordering:
        default_ordering = get_model_default_ordering(queryset_model)

    ordering_fields = [field.replace("-", "") for field in default_ordering]
    direction = "-" if "-" in default_ordering[0] else ""
    if reversed:
        reversed_direction = REVERSED_DIRECTION[direction]
        default_ordering = [f"{reversed_direction}{field}" for field in ordering_fields]

    return queryset.order_by(*default_ordering)
