import binascii
from enum import Enum
from typing import Union

import graphene
from graphene import ObjectType
from graphql import GraphQLError


def from_global_id_or_error(
    id: str, only_type: Union[ObjectType, str, None] = None, field: str = "id"
):
    try:
        _type, _id = graphene.Node.from_global_id(id)
    except (binascii.Error, UnicodeDecodeError, ValueError):
        raise GraphQLError(f"Couldn't resolve id: {id}.")

    if only_type and str(_type) != str(only_type):
        raise GraphQLError(f"Must receive a {only_type} id.")
    return _type, _id


def snake_to_camel_case(name):
    if isinstance(name, str):
        split_name = name.split("_")
        return split_name[0] + "".join(map(str.capitalize, split_name[1:]))
    return name


DJANGO_VALIDATORS_ERROR_CODES = [
    "invalid",
    "invalid_extension",
    "limit_value",
    "max_decimal_places",
    "max_digits",
    "max_length",
    "max_value",
    "max_whole_digits",
    "min_length",
    "min_value",
    "null_characters_not_allowed",
]

DJANGO_FORM_FIELDS_ERROR_CODES = [
    "contradiction",
    "empty",
    "incomplete",
    "invalid_choice",
    "invalid_date",
    "invalid_image",
    "invalid_list",
    "invalid_time",
    "missing",
    "overflow",
]


def get_error_code_from_error(error) -> str:
    code = error.code
    if code in ["required", "blank", "null"]:
        return "required"
    if code in ["unique", "unique_for_date"]:
        return "unique"
    if code in DJANGO_VALIDATORS_ERROR_CODES or code in DJANGO_FORM_FIELDS_ERROR_CODES:
        return "invalid"
    if isinstance(code, Enum):
        code = code.value
    return code
