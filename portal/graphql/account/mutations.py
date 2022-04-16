import graphene
from django.forms import ValidationError
from graphql_jwt.decorators import token_auth

from portal.graphql.core.mutations import BaseMutation

from .types import User


class ObtainJSONWebToken(BaseMutation):
    user = graphene.Field(User)
    token = graphene.String()

    class Arguments:
        email = graphene.String()
        password = graphene.String()

    @classmethod
    @token_auth
    def resolve(cls, root, info, **kwargs):
        return cls(user=info.context.user)

    @classmethod
    def perform_mutation(cls, root, info, **data):
        try:
            response = cls.resolve(root, info, **data)
        except Exception as e:
            return cls.handle_errors(ValidationError(str(e)))
        return response
