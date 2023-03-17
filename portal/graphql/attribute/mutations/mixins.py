from django.core.exceptions import ValidationError
from django.utils.text import slugify
from text_unidecode import unidecode

from ....attribute import ATTRIBUTE_PROPERTIES_CONFIGURATION, AttributeInputType
from ....attribute import models as models
from ...core.utils import validate_slug_and_generate_if_needed


class AttributeMixin:
    ATTRIBUTE_VALUES_FIELD: str
    ONLY_SWATCH_FIELDS = ["file_url", "value"]

    @classmethod
    def clean_values(cls, cleaned_input, attribute):
        values_input = cleaned_input.get(cls.ATTRIBUTE_VALUES_FIELD)
        attribute_input_type = cleaned_input.get("input_type") or attribute.input_type

        if values_input is None:
            return

        if (
            values_input
            and attribute_input_type not in AttributeInputType.TYPES_WITH_CHOICES
        ):
            raise ValidationError(
                {
                    cls.ATTRIBUTE_VALUES_FIELD: ValidationError(
                        f"Values cannot be used with input type {attribute_input_type}."
                    )
                }
            )

        is_swatch_attr = attribute_input_type == AttributeInputType.SWATCH
        for value_data in values_input:
            cls._validate_value(attribute, value_data, is_swatch_attr)

        cls.check_values_are_unique(values_input, attribute)

    @classmethod
    def _validate_value(
        cls,
        attribute: models.Attribute,
        value_data: dict,
        is_swatch_attr: bool,
    ):
        value = value_data.get("name")
        if value is None:
            raise ValidationError(
                {
                    cls.ATTRIBUTE_VALUES_FIELD: ValidationError(
                        "The name field is required."
                    )
                }
            )

        if is_swatch_attr:
            cls.validate_swatch_attr_value(value_data)
        else:
            cls.validate_non_swatch_attr_value(value_data)

        slug_value = value
        value_data["slug"] = slugify(unidecode(slug_value))

        attribute_value = models.AttributeValue(**value_data, attribute=attribute)
        try:
            attribute_value.full_clean()
        except ValidationError as validation_errors:
            for field, err in validation_errors.error_dict.items():
                if field == "attribute":
                    continue
                errors = []
                for error in err:
                    error.code = "invalid"
                    errors.append(error)
                raise ValidationError({cls.ATTRIBUTE_VALUES_FIELD: errors})

    @classmethod
    def validate_non_swatch_attr_value(cls, value_data: dict):
        if any([value_data.get(field) for field in cls.ONLY_SWATCH_FIELDS]):
            raise ValidationError(
                {
                    cls.ATTRIBUTE_VALUES_FIELD: ValidationError(
                        "Cannot define value, file and contentType fields for not swatch attribute."
                    )
                }
            )

    @classmethod
    def validate_swatch_attr_value(cls, value_data: dict):
        if value_data.get("value") and value_data.get("file_url"):
            raise ValidationError(
                {
                    cls.ATTRIBUTE_VALUES_FIELD: ValidationError(
                        "Cannot specify both value and file for swatch attribute."
                    )
                }
            )

    @classmethod
    def check_values_are_unique(cls, values_input: dict, attribute: models.Attribute):
        existing_values = attribute.values.values_list("slug", flat=True)
        for value_data in values_input:
            slug = slugify(unidecode(value_data["name"]))
            if slug in existing_values:
                msg = (
                    f'Value {value_data["name"]} already exists within this attribute.'
                )
                raise ValidationError(
                    {cls.ATTRIBUTE_VALUES_FIELD: ValidationError(msg)}
                )

        new_slugs = [
            slugify(unidecode(value_data["name"])) for value_data in values_input
        ]
        if len(set(new_slugs)) != len(new_slugs):
            raise ValidationError(
                {
                    cls.ATTRIBUTE_VALUES_FIELD: ValidationError(
                        "Provided values are not unique."
                    )
                }
            )

    @classmethod
    def clean_attribute(cls, instance, cleaned_input):
        try:
            cleaned_input = validate_slug_and_generate_if_needed(
                instance, "name", cleaned_input
            )
        except ValidationError as error:
            raise ValidationError({"slug": "required"})
        cls._clean_attribute_settings(instance, cleaned_input)

        return cleaned_input

    @classmethod
    def _clean_attribute_settings(cls, instance, cleaned_input):
        """Validate attributes settings.

        Ensure that any invalid operations will be not performed.
        """
        attribute_input_type = cleaned_input.get("input_type") or instance.input_type
        errors = {}
        for field in ATTRIBUTE_PROPERTIES_CONFIGURATION.keys():
            allowed_input_type = ATTRIBUTE_PROPERTIES_CONFIGURATION[field]
            if attribute_input_type not in allowed_input_type and cleaned_input.get(
                field
            ):
                errors[field] = ValidationError(
                    f"Cannot set {field} on a {attribute_input_type} attribute."
                )
        if errors:
            raise ValidationError(errors)

    @classmethod
    def _save_m2m(cls, info, attribute, cleaned_data):
        super()._save_m2m(info, attribute, cleaned_data)  # type: ignore[misc] # mixin
        values = cleaned_data.get(cls.ATTRIBUTE_VALUES_FIELD) or []
        for value in values:
            attribute.values.create(**value)
