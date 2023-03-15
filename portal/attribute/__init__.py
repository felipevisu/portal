class AttributeInputType:
    """The type that we expect to render the attribute's values as."""

    DROPDOWN = "dropdown"
    MULTISELECT = "multiselect"
    FILE = "file"
    NUMERIC = "numeric"
    PLAIN_TEXT = "plain-text"
    SWATCH = "swatch"
    BOOLEAN = "boolean"
    DATE = "date"
    DATE_TIME = "date-time"

    CHOICES = [
        (DROPDOWN, "Dropdown"),
        (MULTISELECT, "Multi Select"),
        (FILE, "File"),
        (NUMERIC, "Numeric"),
        (PLAIN_TEXT, "Plain Text"),
        (SWATCH, "Swatch"),
        (BOOLEAN, "Boolean"),
        (DATE, "Date"),
        (DATE_TIME, "Date Time"),
    ]

    # list of the input types that can be used in variant selection
    ALLOWED_IN_VARIANT_SELECTION = [DROPDOWN, BOOLEAN, SWATCH, NUMERIC]

    TYPES_WITH_CHOICES = [
        DROPDOWN,
        MULTISELECT,
        SWATCH,
    ]

    # list of the input types that are unique per instances
    TYPES_WITH_UNIQUE_VALUES = [
        FILE,
        PLAIN_TEXT,
        NUMERIC,
        DATE,
        DATE_TIME,
    ]


class AttributeType:
    ENTRY = "entry"
    DOCUMENT = "document"

    CHOICES = [(ENTRY, "Cadastri"), (DOCUMENT, "Documento")]


class AttributeEntryType:
    VEHICLE = "vehicle"
    PROVIDER = "provider"
    VEHICLE_AND_PROVIDER = "vehicle_and_provider"

    CHOICES = [
        (VEHICLE, "Veículo"),
        (PROVIDER, "Fornecedor"),
        (VEHICLE_AND_PROVIDER, "Veículo e fornecedor"),
    ]
