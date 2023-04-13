class AttributeInputType:
    """The type that we expect to render the attribute's values as."""

    DROPDOWN = "dropdown"
    MULTISELECT = "multiselect"
    FILE = "file"
    PLAIN_TEXT = "plain-text"
    SWATCH = "swatch"
    BOOLEAN = "boolean"
    DATE = "date"
    REFERENCE = "reference"

    CHOICES = [
        (DROPDOWN, "Dropdown"),
        (MULTISELECT, "Multi Select"),
        (FILE, "File"),
        (PLAIN_TEXT, "Plain Text"),
        (SWATCH, "Swatch"),
        (BOOLEAN, "Boolean"),
        (DATE, "Date"),
        (REFERENCE, "Referência"),
    ]

    # list of the input types that can be used in variant selection
    ALLOWED_IN_VARIANT_SELECTION = [DROPDOWN, BOOLEAN, SWATCH]

    TYPES_WITH_CHOICES = [
        DROPDOWN,
        MULTISELECT,
        SWATCH,
    ]

    # list of the input types that are unique per instances
    TYPES_WITH_UNIQUE_VALUES = [FILE, REFERENCE, PLAIN_TEXT, DATE]


class AttributeType:
    DOCUMENT = "document"
    VEHICLE = "vehicle"
    PROVIDER = "provider"
    VEHICLE_AND_PROVIDER = "vehicle_and_provider"

    CHOICES = [
        (DOCUMENT, "document"),
        (VEHICLE, "vehicle"),
        (PROVIDER, "provider"),
        (VEHICLE_AND_PROVIDER, "vehicle and provider"),
    ]


class AttributeEntityType:
    VEHICLE = "vehicle"
    PROVIDER = "provider"

    CHOICES = [
        (VEHICLE, "vehicle"),
        (PROVIDER, "provider"),
    ]


ATTRIBUTE_PROPERTIES_CONFIGURATION = {
    "filterable_in_website": [
        AttributeInputType.DROPDOWN,
        AttributeInputType.MULTISELECT,
        AttributeInputType.SWATCH,
        AttributeInputType.BOOLEAN,
        AttributeInputType.DATE,
    ],
    "filterable_in_dashboard": [
        AttributeInputType.DROPDOWN,
        AttributeInputType.MULTISELECT,
        AttributeInputType.SWATCH,
        AttributeInputType.BOOLEAN,
        AttributeInputType.DATE,
    ],
}
