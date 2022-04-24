import graphene
from graphene.types.objecttype import ObjectTypeOptions


class Error(graphene.ObjectType):
    field = graphene.String(
        description=(
            "Name of a field that caused the error. A value of `null` indicates that "
            "the error isn't associated with a particular field."
        ),
        required=False,
    )
    message = graphene.String(description="The error message.")
    code = graphene.String(description="The error code.")

    class Meta:
        description = "Represents an error in the input of a mutation."


class Upload(graphene.types.Scalar):
    class Meta:
        description = (
            "Variables of this type must be set to null in mutations. They will be "
            "replaced with a filename from a following multipart part containing "
            "a binary file. "
            "See: https://github.com/jaydenseric/graphql-multipart-request-spec."
        )

    @staticmethod
    def serialize(value):
        return value

    @staticmethod
    def parse_literal(node):
        return node

    @staticmethod
    def parse_value(value):
        return value


class Permission(graphene.ObjectType):
    code = graphene.String(description="Internal code for permission.", required=True)
    name = graphene.String(
        description="Describe action(s) allowed to do by permission.", required=True
    )

    class Meta:
        description = "Represents a permission object in a friendly form."


class OrderDirection(graphene.Enum):
    ASC = ""
    DESC = "-"


class SortInputMeta(ObjectTypeOptions):
    sort_enum = None


class SortInputObjectType(graphene.InputObjectType):
    direction = graphene.Argument(OrderDirection, required=True)

    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(
        cls, container=None, _meta=None, sort_enum=None, type_name=None, **options
    ):
        if not _meta:
            _meta = SortInputMeta(cls)
        if sort_enum:
            _meta.sort_enum = sort_enum

        super().__init_subclass_with_meta__(container, _meta, **options)
        if sort_enum and type_name:
            field = graphene.Argument(
                sort_enum,
                required=True,
                description=f"Sort {type_name} by the selected field.",
            )
            cls._meta.fields.update({"field": field})
