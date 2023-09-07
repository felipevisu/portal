import graphene

from .mutations.authentication import (
    CreateToken,
    DeactivateAllUserTokens,
    RefreshToken,
    VerifyToken,
)
from .mutations.base import RequestPasswordReset, SetPassword
from .types import User


class Query(graphene.ObjectType):
    me = graphene.Field(User)

    def resolve_me(self, info):
        user = info.context.user
        return user


class Mutation(graphene.ObjectType):
    token_create = CreateToken.Field()
    token_refresh = RefreshToken.Field()
    token_verify = VerifyToken.Field()
    tokens_deactivate_all = DeactivateAllUserTokens.Field()
    request_password_reset = RequestPasswordReset.Field()
    password_reset = SetPassword.Field()
