import graphene


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
