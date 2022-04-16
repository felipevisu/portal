import graphene
import graphql_jwt

from .mutations import ObtainJSONWebToken
from .types import User


class Query(graphene.ObjectType):
    me = graphene.Field(User)

    def resolve_me(self, info):
        user = info.context.user
        return user if user.is_authenticated else None


class Mutation(graphene.ObjectType):
    token_auth = ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
