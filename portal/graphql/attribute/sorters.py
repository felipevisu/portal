import graphene

from ..core.types.sort_input import SortInputObjectType


class AttributeSortField(graphene.Enum):
    NAME = ["name", "slug"]
    SLUG = ["slug"]
    VALUE_REQUIRED = ["value_required", "name", "slug"]
    VISIBLE_IN_WEBSITE = ["visible_in_website", "name", "slug"]
    FILTERABLE_IN_WEBSITE = ["filterable_in_website", "name", "slug"]
    FILTERABLE_IN_DASHBOARD = ["filterable_in_dashboard", "name", "slug"]

    @property
    def description(self):
        # pylint: disable=no-member
        descriptions = {
            AttributeSortField.NAME.name: "Sort attributes by name",  # type: ignore[attr-defined] # graphene.Enum is not typed # noqa: E501
            AttributeSortField.SLUG.name: "Sort attributes by slug",  # type: ignore[attr-defined] # graphene.Enum is not typed # noqa: E501
            AttributeSortField.VALUE_REQUIRED.name: (  # type: ignore[attr-defined] # graphene.Enum is not typed # noqa: E501
                "Sort attributes by the value required flag"
            ),
            AttributeSortField.VISIBLE_IN_WEBSITE.name: (  # type: ignore[attr-defined] # graphene.Enum is not typed # noqa: E501
                "Sort attributes by visibility in the storefront"
            ),
            AttributeSortField.FILTERABLE_IN_WEBSITE.name: (  # type: ignore[attr-defined] # graphene.Enum is not typed # noqa: E501
                "Sort attributes by the filterable in storefront flag"
            ),
            AttributeSortField.FILTERABLE_IN_DASHBOARD.name: (  # type: ignore[attr-defined] # graphene.Enum is not typed # noqa: E501
                "Sort attributes by the filterable in dashboard flag"
            ),
        }
        if self.name in descriptions:
            return descriptions[self.name]
        raise ValueError(f"Unsupported enum value: {self.value}")


class AttributeSortingInput(SortInputObjectType):
    class Meta:
        sort_enum = AttributeSortField
        type_name = "attributes"


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
