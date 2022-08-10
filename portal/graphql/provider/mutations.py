import graphene
from django.core.exceptions import ValidationError

from ...core.permissions import ProviderPermissions
from ...provider import models
from ..core.mutations import ModelBulkDeleteMutation, ModelDeleteMutation, ModelMutation
from ..core.types import NonNullList
from ..core.utils import validate_slug_and_generate_if_needed
from .types import Provider, Segment


class ProviderInput(graphene.InputObjectType):
    name = graphene.String()
    slug = graphene.String()
    document_number = graphene.String()
    segment = graphene.ID()
    is_published = graphene.Boolean(default=False)
    publication_date = graphene.Date(required=False)


class ProviderCreate(ModelMutation):
    provider = graphene.Field(Provider)

    class Arguments:
        input = ProviderInput(required=True)

    class Meta:
        model = models.Provider
        permissions = (ProviderPermissions.MANAGE_PROVIDERS,)

    @classmethod
    def clean_input(cls, info, instance, data, input_cls=None):
        cleaned_input = super().clean_input(info, instance, data, input_cls)
        try:
            cleaned_input = validate_slug_and_generate_if_needed(
                instance, "name", cleaned_input
            )
        except ValidationError as error:
            raise ValidationError({"slug": error})
        return cleaned_input


class ProviderUpdate(ModelMutation):
    vehicle = graphene.Field(Provider)

    class Arguments:
        id = graphene.ID()
        input = ProviderInput(required=True)

    class Meta:
        model = models.Provider
        permissions = (ProviderPermissions.MANAGE_PROVIDERS,)


class ProviderDelete(ModelDeleteMutation):

    class Arguments:
        id = graphene.ID()

    class Meta:
        model = models.Provider
        permissions = (ProviderPermissions.MANAGE_PROVIDERS,)


class ProviderBulkDelete(ModelBulkDeleteMutation):
    class Arguments:
        ids = NonNullList(
            graphene.ID, required=True, description="List of providers IDs to delete."
        )

    class Meta:
        description = "Deletes providers."
        model = models.Provider
        object_type = Provider
        permissions = (ProviderPermissions.MANAGE_PROVIDERS,)


class SegmentInput(graphene.InputObjectType):
    name = graphene.String()
    slug = graphene.String()


class SegmentCreate(ModelMutation):
    segment = graphene.Field(Segment)

    class Arguments:
        input = SegmentInput(required=True)

    class Meta:
        model = models.Segment
        permissions = (ProviderPermissions.MANAGE_SEGMENTS,)

    @classmethod
    def clean_input(cls, info, instance, data, input_cls=None):
        cleaned_input = super().clean_input(info, instance, data, input_cls)
        try:
            cleaned_input = validate_slug_and_generate_if_needed(
                instance, "name", cleaned_input
            )
        except ValidationError as error:
            raise ValidationError({"slug": error})
        return cleaned_input


class SegmentUpdate(ModelMutation):
    segment = graphene.Field(Segment)

    class Arguments:
        id = graphene.ID()
        input = SegmentInput(required=True)

    class Meta:
        model = models.Segment
        permissions = (ProviderPermissions.MANAGE_SEGMENTS,)


class SegmentDelete(ModelDeleteMutation):

    class Arguments:
        id = graphene.ID()

    class Meta:
        model = models.Segment
        permissions = (ProviderPermissions.MANAGE_SEGMENTS,)


class SegmentBulkDelete(ModelBulkDeleteMutation):
    class Arguments:
        ids = NonNullList(
            graphene.ID, required=True, description="List of segments IDs to delete."
        )

    class Meta:
        description = "Deletes segments."
        model = models.Segment
        object_type = Segment
        permissions = (ProviderPermissions.MANAGE_SEGMENTS,)
