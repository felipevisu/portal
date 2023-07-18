from django.utils.crypto import get_random_string

from portal.graphql.core.mutations import BaseMutation


class DeactivateAllUserTokens(BaseMutation):
    class Meta:
        description = "Deactivate all JWT tokens of the currently authenticated user."

    @classmethod
    def check_permissions(cls, context):
        return context.user.is_authenticated

    @classmethod
    def perform_mutation(cls, root, info, **data):
        user = info.context.user
        user.jwt_token_key = get_random_string()
        user.save(update_fields=["jwt_token_key"])
        return cls()
