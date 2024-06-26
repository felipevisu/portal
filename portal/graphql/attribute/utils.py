import datetime
from collections import defaultdict
from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, Iterable, List, Optional, Tuple, Union

import graphene
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.db.models.expressions import Exists, OuterRef
from django.template.defaultfilters import truncatechars
from django.utils import timezone
from django.utils.text import slugify
from graphql.error import GraphQLError
from text_unidecode import unidecode

from portal.attribute.utils import associate_attribute_values_to_instance
from portal.graphql.utils import get_nodes

from ...attribute import AttributeInputType
from ...attribute import models as attribute_models
from ...core.utils import prepare_unique_slug
from ...entry import models as entry_models
from ..core.utils import from_global_id_or_error

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from ...attribute.models import Attribute


def get_duplicated_values(values):
    """Return set of duplicated values."""
    return {value for value in values if values.count(value) > 1}


@dataclass
class AttrValuesForSelectableFieldInput:
    id: Optional[str] = None
    value: Optional[str] = None


@dataclass
class AttrValuesInput:
    global_id: str
    values: Optional[List[str]] = None
    dropdown: Optional[AttrValuesForSelectableFieldInput] = None
    multiselect: Optional[List[AttrValuesForSelectableFieldInput]] = None
    plain_text: Optional[str] = None
    boolean: Optional[bool] = None
    date: Optional[datetime.date] = None
    references: Union[List[str], List[entry_models.Entry], None] = None


T_INSTANCE = entry_models.Entry
T_INPUT_MAP = List[Tuple[attribute_models.Attribute, AttrValuesInput]]
T_ERROR_DICT = Dict[Tuple[str, str], List[str]]


class AttributeAssignmentMixin:
    @classmethod
    def _resolve_attribute_nodes(
        cls,
        qs: "QuerySet",
        *,
        global_ids: List[str],
        pks: Iterable[int],
    ):
        """Retrieve attributes nodes from given global IDs."""
        qs = qs.filter(pk__in=pks)
        nodes: List[attribute_models.Attribute] = list(qs)

        if not nodes:
            raise ValidationError((f"Could not resolve to a node: ids={global_ids}."))

        nodes_pk_list = set()
        for node in nodes:
            nodes_pk_list.add(node.pk)

        for pk, global_id in zip(pks, global_ids):
            if pk not in nodes_pk_list:
                raise ValidationError(f"Could not resolve {global_id!r} to Attribute")

        return nodes

    @classmethod
    def _resolve_attribute_global_id(cls, global_id: str) -> int:
        """Resolve an Attribute global ID into an internal ID (int)."""
        try:
            graphene_type, internal_id = from_global_id_or_error(
                global_id, only_type="Attribute"
            )
        except GraphQLError as e:
            raise ValidationError(str(e))
        if not internal_id.isnumeric():
            raise ValidationError(f"An invalid ID value was passed: {global_id}")
        return int(internal_id)

    @classmethod
    def _get_assigned_attribute_value_if_exists(
        cls,
        instance: T_INSTANCE,
        attribute: attribute_models.Attribute,
        lookup_field: str,
        value,
    ):
        assigned_values = attribute_models.AssignedEntryAttributeValue.objects.filter(
            entry_id=instance.pk
        )

        return attribute_models.AttributeValue.objects.filter(
            Exists(assigned_values.filter(value_id=OuterRef("id"))),
            attribute_id=attribute.pk,
            **{lookup_field: value},
        ).first()

    @classmethod
    def clean_input(
        cls,
        raw_input: dict,
        attributes_qs: "QuerySet",
        creation: bool = True,
    ) -> T_INPUT_MAP:
        pks = {}
        global_ids = []

        for attribute_input in raw_input:
            global_id = attribute_input.pop("id", None)
            if global_id is None:
                raise ValidationError("The attribute ID is required.")
            values = AttrValuesInput(
                global_id=global_id,
                values=attribute_input.pop("values", []),
                **attribute_input,
            )

            internal_id = cls._resolve_attribute_global_id(global_id)
            global_ids.append(global_id)
            pks[internal_id] = values

        attributes = cls._resolve_attribute_nodes(
            attributes_qs, global_ids=global_ids, pks=pks.keys()
        )
        attr_with_invalid_references = []
        cleaned_input = []
        for attribute in attributes:
            key = pks[attribute.pk]
            if attribute.input_type == AttributeInputType.REFERENCE:
                try:
                    key = cls._validate_references(attribute, key)
                except GraphQLError:
                    attr_with_invalid_references.append(attribute)

            cleaned_input.append((attribute, key))

        if attr_with_invalid_references:
            raise ValidationError(
                "Provided references are invalid. Some of the nodes "
                "do not exist or are different types than types defined "
                "in attribute entity type.",
            )

        cls._validate_attributes_input(
            cleaned_input,
            attributes_qs,
            creation=creation,
        )
        return cleaned_input

    @classmethod
    def _validate_attributes_input(
        cls, cleaned_input: T_INPUT_MAP, attribute_qs: "QuerySet", *, creation: bool
    ):
        if errors := validate_attributes_input(
            cleaned_input,
            attribute_qs,
            creation=creation,
        ):
            raise ValidationError(errors)

    @classmethod
    def _validate_references(
        cls, attribute: attribute_models.Attribute, values: AttrValuesInput
    ) -> AttrValuesInput:
        references = values.references
        if not references:
            return values

        if not attribute.entity_type:
            # FIXME: entity type is nullable for whatever reason
            raise ValidationError("Invalid reference type.")
        try:
            ref_instances = get_nodes(
                references, attribute.entity_type, model=entry_models.Entry
            )
            values.references = ref_instances
            return values
        except GraphQLError:
            raise ValidationError("Invalid reference type.")

    @classmethod
    def save(cls, instance: T_INSTANCE, cleaned_input: T_INPUT_MAP):
        pre_save_methods_mapping = {
            AttributeInputType.BOOLEAN: cls._pre_save_boolean_values,
            AttributeInputType.DATE: cls._pre_save_date_time_values,
            AttributeInputType.DROPDOWN: cls._pre_save_dropdown_value,
            AttributeInputType.MULTISELECT: cls._pre_save_multiselect_values,
            AttributeInputType.PLAIN_TEXT: cls._pre_save_plain_text_values,
            AttributeInputType.REFERENCE: cls._pre_save_reference_values,
        }
        for attribute, attr_values in cleaned_input:
            is_handled_by_values_field = (
                attr_values.values
                and attribute.input_type
                in (AttributeInputType.DROPDOWN, AttributeInputType.MULTISELECT)
            )
            if is_handled_by_values_field:
                attribute_values = cls._pre_save_values(attribute, attr_values)
            else:
                pre_save_func = pre_save_methods_mapping[attribute.input_type]
                attribute_values = pre_save_func(instance, attribute, attr_values)

            associate_attribute_values_to_instance(
                instance, attribute, *attribute_values
            )

    @classmethod
    def _pre_save_dropdown_value(
        cls,
        _,
        attribute: attribute_models.Attribute,
        attr_values: AttrValuesInput,
    ):
        if not attr_values.dropdown:
            return tuple()

        if id := attr_values.dropdown.id:
            _, attr_value_id = from_global_id_or_error(id)
            model = attribute_models.AttributeValue.objects.get(pk=attr_value_id)
            if not model:
                raise ValidationError("Attribute value with given ID can't be found")
            return (model,)

        if attr_value := attr_values.dropdown.value:
            model = prepare_attribute_values(attribute, [attr_value])
            return model

        return tuple()

    @classmethod
    def _pre_save_multiselect_values(
        cls,
        _,
        attribute: attribute_models.Attribute,
        attr_values_input: AttrValuesInput,
    ):
        if not attr_values_input.multiselect:
            return tuple()

        attribute_values: List[attribute_models.AttributeValue] = []
        for attr_value in attr_values_input.multiselect:
            if attr_value.id:
                _, attr_value_id = from_global_id_or_error(attr_value.id)
                attr_value_model = attribute_models.AttributeValue.objects.get(
                    pk=attr_value_id
                )
                if not attr_value_model:
                    raise ValidationError(
                        "Attribute value with given ID can't be found"
                    )
                if attr_value_model.id not in [a.id for a in attribute_values]:
                    attribute_values.append(attr_value_model)

            if attr_value.value:
                attr_value_model = prepare_attribute_values(
                    attribute, [attr_value.value]
                )[0]
                if attr_value_model.id not in [a.id for a in attribute_values]:
                    attribute_values.append(attr_value_model)

        return attribute_values

    @classmethod
    def _pre_save_reference_values(
        cls,
        instance,
        attribute: attribute_models.Attribute,
        attr_values: AttrValuesInput,
    ):
        """Lazy-retrieve or create the database objects from the supplied raw values.

        Slug value is generated based on instance and reference entity id.
        """
        if not attr_values.references or not attribute.entity_type:
            return tuple()

        get_or_create = attribute.values.get_or_create

        reference_list = []
        attr_value_field = "reference"
        for ref in attr_values.references:
            name = getattr(ref, "name")
            reference_list.append(
                get_or_create(
                    attribute=attribute,
                    slug=slugify(unidecode(f"{instance.id}_{ref.id}")),  # type: ignore
                    defaults={"name": name},
                    **{attr_value_field: ref},
                )[0]
            )
        return tuple(reference_list)

    @classmethod
    def _pre_save_values(
        cls, attribute: attribute_models.Attribute, attr_values: AttrValuesInput
    ):
        if not attr_values.values:
            return tuple()
        result = prepare_attribute_values(attribute, attr_values.values)
        return tuple(result)

    @classmethod
    def _pre_save_plain_text_values(
        cls,
        instance: T_INSTANCE,
        attribute: attribute_models.Attribute,
        attr_values: AttrValuesInput,
    ):
        if not attr_values.plain_text:
            return tuple()
        defaults = {
            "plain_text": attr_values.plain_text,
            "name": truncatechars(attr_values.plain_text, 200),
        }
        return cls._update_or_create_value(instance, attribute, defaults)

    @classmethod
    def _pre_save_boolean_values(
        cls,
        instance: T_INSTANCE,
        attribute: attribute_models.Attribute,
        attr_values: AttrValuesInput,
    ):
        if attr_values.boolean is None:
            return tuple()
        get_or_create = attribute.values.get_or_create
        boolean = bool(attr_values.boolean)
        value, _ = get_or_create(
            attribute=attribute,
            slug=slugify(unidecode(f"{attribute.id}_{boolean}")),
            defaults={
                "name": f"{attribute.name}: {'Yes' if boolean else 'No'}",
                "boolean": boolean,
            },
        )
        return (value,)

    @classmethod
    def _pre_save_date_time_values(
        cls,
        instance: T_INSTANCE,
        attribute: attribute_models.Attribute,
        attr_values: AttrValuesInput,
    ):
        is_date_attr = attribute.input_type == AttributeInputType.DATE
        tz = timezone.utc
        if is_date_attr:
            if not attr_values.date:
                return ()
            value = str(attr_values.date)
            date_time = datetime.datetime(
                attr_values.date.year,
                attr_values.date.month,
                attr_values.date.day,
                0,
                0,
                tzinfo=tz,
            )
        else:
            if not attr_values.date_time:
                return ()
            value = str(attr_values.date_time)
            date_time = attr_values.date_time
        defaults = {"name": value, "date_time": date_time}
        return cls._update_or_create_value(instance, attribute, defaults)

    @classmethod
    def _update_or_create_value(
        cls,
        instance: T_INSTANCE,
        attribute: attribute_models.Attribute,
        value_defaults: dict,
    ):
        update_or_create = attribute.values.update_or_create
        slug = slugify(unidecode(f"{instance.id}_{attribute.id}"))
        value, _created = update_or_create(
            attribute=attribute,
            slug=slug,
            defaults=value_defaults,
        )
        return (value,)


def prepare_attribute_values(attribute: attribute_models.Attribute, values: List[str]):
    slug_to_value_map = {}
    name_to_value_map = {}
    for val in attribute.values.filter(Q(name__in=values) | Q(slug__in=values)):
        slug_to_value_map[val.slug] = val
        name_to_value_map[val.name] = val

    existing_slugs = get_existing_slugs(attribute, values)

    result = []
    values_to_create = []
    for value in values:
        # match the value firstly by slug then by name
        value_obj = slug_to_value_map.get(value) or name_to_value_map.get(value)
        if value_obj:
            result.append(value_obj)
        else:
            slug = prepare_unique_slug(slugify(unidecode(value)), existing_slugs)
            instance = attribute_models.AttributeValue(
                attribute=attribute, name=value, slug=slug
            )
            result.append(instance)

            values_to_create.append(instance)

            # the set of existing slugs must be updated to not generate accidentally
            # the same slug for two or more values
            existing_slugs.add(slug)

            # extend name to slug value to not create two elements with the same name
            name_to_value_map[instance.name] = instance

    attribute_models.AttributeValue.objects.bulk_create(values_to_create)
    return result


def get_existing_slugs(attribute: attribute_models.Attribute, values: List[str]):
    lookup = Q()
    for value in values:
        lookup |= Q(slug__startswith=slugify(unidecode(value)))

    existing_slugs = set(attribute.values.filter(lookup).values_list("slug", flat=True))
    return existing_slugs


class AttributeInputErrors:
    """Define error message and error code for given error.

    All used error codes must be specified in PageErrorCode and ProductErrorCode.
    """

    ERROR_NO_VALUE_GIVEN = (
        "Attribute expects a value but none were given.",
        "REQUIRED",
    )
    ERROR_MORE_THAN_ONE_VALUE_GIVEN = (
        "Attribute must take only one value.",
        "INVALID",
    )
    ERROR_BLANK_VALUE = (
        "Attribute values cannot be blank.",
        "REQUIRED",
    )
    ERROR_DUPLICATED_VALUES = (
        "Duplicated attribute values are provided.",
        "DUPLICATED_INPUT_ITEM",
    )
    ERROR_ID_AND_VALUE = (
        "Attribute values cannot be assigned by both id and value.",
        "INVALID",
    )
    # file errors
    ERROR_NO_FILE_GIVEN = (
        "Attribute file url cannot be blank.",
        "REQUIRED",
    )
    ERROR_BLANK_FILE_VALUE = (
        "Attribute expects a file url but none were given.",
        "REQUIRED",
    )

    # reference errors
    ERROR_NO_REFERENCE_GIVEN = (
        "Attribute expects an reference but none were given.",
        "REQUIRED",
    )

    # text errors
    ERROR_MAX_LENGTH = (
        "Attribute value length is exceeded.",
        "INVALID",
    )


def validate_attributes_input(
    input_data: List[Tuple["Attribute", "AttrValuesInput"]],
    attribute_qs: "QuerySet",
    *,
    creation: bool,
):
    attribute_errors: T_ERROR_DICT = defaultdict(list)
    input_type_to_validation_func_mapping = {
        AttributeInputType.BOOLEAN: validate_boolean_input,
        AttributeInputType.DATE: validate_date_time_input,
        AttributeInputType.DROPDOWN: validate_dropdown_input,
        AttributeInputType.MULTISELECT: validate_multiselect_input,
        AttributeInputType.PLAIN_TEXT: validate_plain_text_attributes_input,
        AttributeInputType.REFERENCE: validate_reference_attributes_input,
    }

    for attribute, attr_values in input_data:
        attrs = (
            attribute,
            attr_values,
            attribute_errors,
        )
        is_handled_by_values_field = attr_values.values and attribute.input_type in (
            AttributeInputType.DROPDOWN,
            AttributeInputType.MULTISELECT,
        )
        if is_handled_by_values_field:
            validate_standard_attributes_input(*attrs)
        else:
            validation_func = input_type_to_validation_func_mapping[
                attribute.input_type
            ]
            validation_func(*attrs)

    errors = prepare_error_list_from_error_attribute_mapping(attribute_errors)
    # Check if all required attributes are in input only when instance is created.
    # We should allow updating any instance attributes.
    if creation:
        errors = validate_required_attributes(input_data, attribute_qs, errors)
    return errors


def validate_boolean_input(
    attribute: "Attribute",
    attr_values: "AttrValuesInput",
    attribute_errors: T_ERROR_DICT,
):
    attribute_id = attr_values.global_id
    value = attr_values.boolean

    if attribute.value_required and value is None:
        attribute_errors[AttributeInputErrors.ERROR_BLANK_VALUE].append(attribute_id)


def validate_reference_attributes_input(
    attribute: "Attribute",
    attr_values: "AttrValuesInput",
    attribute_errors: T_ERROR_DICT,
):
    attribute_id = attr_values.global_id
    references = attr_values.references
    if not references:
        if attribute.value_required:
            attribute_errors[AttributeInputErrors.ERROR_NO_REFERENCE_GIVEN].append(
                attribute_id
            )


def validate_plain_text_attributes_input(
    attribute: "Attribute",
    attr_values: "AttrValuesInput",
    attribute_errors: T_ERROR_DICT,
):
    attribute_id = attr_values.global_id

    if (
        not attr_values.plain_text or not attr_values.plain_text.strip()
    ) and attribute.value_required:
        attribute_errors[AttributeInputErrors.ERROR_NO_VALUE_GIVEN].append(attribute_id)


def validate_date_time_input(
    attribute: "Attribute",
    attr_values: "AttrValuesInput",
    attribute_errors: T_ERROR_DICT,
):
    is_blank_date = (
        attribute.input_type == AttributeInputType.DATE and not attr_values.date
    )

    if attribute.value_required and is_blank_date:
        attribute_errors[AttributeInputErrors.ERROR_NO_VALUE_GIVEN].append(
            attr_values.global_id
        )


def validate_standard_attributes_input(
    attribute: "Attribute",
    attr_values: "AttrValuesInput",
    attribute_errors: T_ERROR_DICT,
):
    """To be deprecated together with `AttributeValueInput.values` field."""
    attribute_id = attr_values.global_id

    if not attr_values.values:
        if attribute.value_required:
            attribute_errors[AttributeInputErrors.ERROR_NO_VALUE_GIVEN].append(
                attribute_id
            )
    elif (
        attribute.input_type != AttributeInputType.MULTISELECT
        and len(attr_values.values) != 1
    ):
        attribute_errors[AttributeInputErrors.ERROR_MORE_THAN_ONE_VALUE_GIVEN].append(
            attribute_id
        )

    if attr_values.values is not None:
        validate_values(
            attribute_id,
            attribute,
            attr_values.values,
            attribute_errors,
        )


def validate_single_selectable_field(
    attribute: "Attribute",
    attr_value: AttrValuesForSelectableFieldInput,
    attribute_errors: T_ERROR_DICT,
    attribute_id: str,
):
    id = attr_value.id
    value = attr_value.value

    if id and value:
        attribute_errors[AttributeInputErrors.ERROR_ID_AND_VALUE].append(attribute_id)
        return

    if not id and not value and attribute.value_required:
        attribute_errors[AttributeInputErrors.ERROR_NO_VALUE_GIVEN].append(attribute_id)
        return

    if value:
        max_length = attribute.values.model.name.field.max_length  # type: ignore
        if not value.strip():
            attribute_errors[AttributeInputErrors.ERROR_BLANK_VALUE].append(
                attribute_id
            )
        elif len(value) > max_length:
            attribute_errors[AttributeInputErrors.ERROR_MAX_LENGTH].append(attribute_id)

    if id:
        if not id.strip():
            attribute_errors[AttributeInputErrors.ERROR_BLANK_VALUE].append(
                attribute_id
            )


def validate_dropdown_input(
    attribute: "Attribute",
    attr_values: "AttrValuesInput",
    attribute_errors: T_ERROR_DICT,
):
    attribute_id = attr_values.global_id
    if not attr_values.dropdown:
        if attribute.value_required:
            attribute_errors[AttributeInputErrors.ERROR_NO_VALUE_GIVEN].append(
                attribute_id
            )
    else:
        validate_single_selectable_field(
            attribute,
            attr_values.dropdown,
            attribute_errors,
            attribute_id,
        )


def validate_multiselect_input(
    attribute: "Attribute",
    attr_values: "AttrValuesInput",
    attribute_errors: T_ERROR_DICT,
):
    attribute_id = attr_values.global_id
    multi_values = attr_values.multiselect
    if not multi_values:
        if attribute.value_required:
            attribute_errors[AttributeInputErrors.ERROR_NO_VALUE_GIVEN].append(
                attribute_id
            )
    else:
        ids = [value.id for value in multi_values if value.id is not None]
        values = [value.value for value in multi_values if value.value is not None]

        if ids and values:
            attribute_errors[AttributeInputErrors.ERROR_ID_AND_VALUE].append(
                attribute_id
            )
            return

        if not ids and not values and attribute.value_required:
            attribute_errors[AttributeInputErrors.ERROR_NO_VALUE_GIVEN].append(
                attribute_id
            )
            return

        if len(ids) > len(set(ids)) or len(values) > len(set(values)):
            attribute_errors[AttributeInputErrors.ERROR_DUPLICATED_VALUES].append(
                attribute_id
            )
            return

        for attr_value in multi_values:
            validate_single_selectable_field(
                attribute,
                attr_value,
                attribute_errors,
                attribute_id,
            )


def validate_values(
    attribute_id: str,
    attribute: "Attribute",
    values: list,
    attribute_errors: T_ERROR_DICT,
):
    """To be deprecated together with `AttributeValueInput.values` field."""
    name_field = attribute.values.model.name.field  # type: ignore
    if get_duplicated_values(values):
        attribute_errors[AttributeInputErrors.ERROR_DUPLICATED_VALUES].append(
            attribute_id
        )
    for value in values:
        if value is None or not value.strip():
            attribute_errors[AttributeInputErrors.ERROR_BLANK_VALUE].append(
                attribute_id
            )
        elif len(value) > name_field.max_length:
            attribute_errors[AttributeInputErrors.ERROR_MAX_LENGTH].append(attribute_id)


def validate_required_attributes(
    input_data: List[Tuple["Attribute", "AttrValuesInput"]],
    attribute_qs: "QuerySet",
    errors: List[ValidationError],
):
    """Ensure all required attributes are supplied."""

    supplied_attribute_pk = [attribute.pk for attribute, _ in input_data]

    missing_required_attributes = attribute_qs.filter(
        Q(value_required=True) & ~Q(pk__in=supplied_attribute_pk)
    )

    if missing_required_attributes:
        ids = [
            graphene.Node.to_global_id("Attribute", attr.pk)
            for attr in missing_required_attributes
        ]
        error = ValidationError(
            "All attributes flagged as having a value required must be supplied.",
            params={"attributes": ids},
        )
        errors.append(error)

    return errors


def prepare_error_list_from_error_attribute_mapping(attribute_errors: T_ERROR_DICT):
    errors = []
    for error_data, attributes in attribute_errors.items():
        error_msg, error_type = error_data
        error = ValidationError(error_msg, params={"attributes": attributes})
        errors.append(error)

    return errors
