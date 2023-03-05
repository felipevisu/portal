import graphene
from django.core.exceptions import ValidationError
from django.utils.text import slugify

from ...channel import models
from ...core.permissions import ChannelPermissions
from ..core.mutations import BaseMutation, ModelDeleteMutation, ModelMutation
from .types import Channel


class ChannelInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    slug = graphene.String(required=True)
    is_active = graphene.Boolean()


class ChannelCreate(ModelMutation):
    class Arguments:
        input = ChannelInput(required=True)

    class Meta:
        model = models.Channel
        object_type = Channel
        permissions = (ChannelPermissions.MANAGE_CHANNELS,)

    @classmethod
    def get_type_for_model(cls):
        return Channel

    @classmethod
    def clean_input(cls, info, instance, data, **kwargs):
        cleaned_input = super().clean_input(info, instance, data, **kwargs)
        slug = cleaned_input.get("slug")
        if slug:
            cleaned_input["slug"] = slugify(slug)
        return cleaned_input


class ChannelUpdate(ModelMutation):
    class Arguments:
        id = graphene.ID(required=True)
        input = ChannelInput(required=True)

    class Meta:
        model = models.Channel
        object_type = Channel
        permissions = (ChannelPermissions.MANAGE_CHANNELS,)

    @classmethod
    def clean_input(cls, info, instance, data, **kwargs):
        cleaned_input = super().clean_input(info, instance, data, **kwargs)
        slug = cleaned_input.get("slug")
        if slug:
            cleaned_input["slug"] = slugify(slug)
        return cleaned_input


class ChannelDelete(ModelDeleteMutation):
    class Arguments:
        id = graphene.ID(required=True, description="ID of a channel to delete.")

    class Meta:
        model = models.Channel
        object_type = Channel
        permissions = (ChannelPermissions.MANAGE_CHANNELS,)


class ChannelActivate(BaseMutation):
    channel = graphene.Field(Channel)

    class Arguments:
        id = graphene.ID(required=True)

    class Meta:
        permissions = (ChannelPermissions.MANAGE_CHANNELS,)

    @classmethod
    def clean_channel_availability(cls, channel):
        if channel.is_active:
            raise ValidationError(
                {"id": ValidationError("This channel is already activated.")}
            )

    @classmethod
    def perform_mutation(cls, _root, info, /, **data):
        channel = cls.get_node_or_error(info, data["id"], only_type=Channel)
        cls.clean_channel_availability(channel)
        channel.is_active = True
        channel.save(update_fields=["is_active"])
        return ChannelActivate(channel=channel)


class ChannelDeactivate(BaseMutation):
    channel = graphene.Field(Channel)

    class Arguments:
        id = graphene.ID(required=True)

    class Meta:
        permissions = (ChannelPermissions.MANAGE_CHANNELS,)

    @classmethod
    def clean_channel_availability(cls, channel):
        if channel.is_active is False:
            raise ValidationError(
                {"id": ValidationError("This channel is already deactivated.")}
            )

    @classmethod
    def perform_mutation(cls, _root, info, /, **data):
        channel = cls.get_node_or_error(info, data["id"], only_type=Channel)
        cls.clean_channel_availability(channel)
        channel.is_active = False
        channel.save(update_fields=["is_active"])
        return ChannelDeactivate(channel=channel)
