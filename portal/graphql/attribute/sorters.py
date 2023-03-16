import graphene

from ..core.types.sort_input import SortInputObjectType


class AttributeChoicesSortField(graphene.Enum):
    NAME = ["name", "slug"]
    SLUG = ["slug"]

    @property
    def description(self):
        descriptions = {
            AttributeChoicesSortField.NAME.name: "Sort attribute choice by name.",  # type: ignore[attr-defined] # graphene.Enum is not typed # noqa: E501
            AttributeChoicesSortField.SLUG.name: "Sort attribute choice by slug.",  # type: ignore[attr-defined] # graphene.Enum is not typed # noqa: E501
        }
        if self.name in descriptions:
            return descriptions[self.name]
        raise ValueError(f"Unsupported enum value: {self.value}")


class AttributeChoicesSortingInput(SortInputObjectType):
    class Meta:
        sort_enum = AttributeChoicesSortField
        type_name = "attribute choices"
