import graphene

from ...attribute import AttributeEntryType, AttributeInputType, AttributeType
from ..core.enums import str_to_enum, to_enum

AttributeInputTypeEnum = to_enum(AttributeInputType)
AttributeTypeEnum = to_enum(AttributeType)
AttributeEntryTypeEnum = to_enum(AttributeEntryType)

AttributeEntryTypeEnum = graphene.Enum(
    "AttributeEntryTypeEnum",
    [(str_to_enum(name.upper()), code) for code, name in AttributeEntryType.CHOICES],
)
