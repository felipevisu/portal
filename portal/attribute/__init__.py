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
    ENTRY_TYPE = "entry_type"

    CHOICES = [
        (ENTRY_TYPE, "Entry Type"),
    ]


class AttributeEntityType:
    ENTRY = "entry"

    CHOICES = [
        (ENTRY, "Entry"),
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
