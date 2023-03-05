from typing import Type, TypeVar, Union, cast

import graphene
from django.db.models import Model
from graphene.types.resolver import get_default_resolver

from ...channel import models
from ..core.types import ModelObjectType


class Channel(ModelObjectType):
    id = graphene.GlobalID(required=True)
    name = graphene.String(
        description="Name of the channel.",
        required=True,
    )
    slug = graphene.String(
        required=True,
        description="Slug of the channel.",
    )
    is_active = graphene.Boolean(
        description="Whether the channel is active.",
        required=True,
    )

    class Meta:
        description = "Represents channel."
        model = models.Channel
        interfaces = [graphene.relay.Node]
