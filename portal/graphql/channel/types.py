from typing import Type, TypeVar, Union, cast

import graphene
from django.db.models import Model
from graphene.types.resolver import get_default_resolver

from ...channel import models
from ..core import ResolveInfo
from ..core.types import ModelObjectType
from . import ChannelContext

T = TypeVar("T", bound=Model)


class ChannelContextTypeForObjectType(ModelObjectType[T]):
    class Meta:
        abstract = True

    @staticmethod
    def resolver_with_context(
        attname, default_value, root: ChannelContext, info: ResolveInfo, **args
    ):
        resolver = get_default_resolver()
        return resolver(attname, default_value, root.node, info, **args)

    @staticmethod
    def resolve_id(root: ChannelContext[T], _info: ResolveInfo):
        return root.node.pk


class ChannelContextType(ChannelContextTypeForObjectType[T]):
    class Meta:
        abstract = True

    @classmethod
    def is_type_of(cls, root: Union[ChannelContext[T], T], _info: ResolveInfo) -> bool:
        # Unwrap node from ChannelContext if it didn't happen already
        if isinstance(root, ChannelContext):
            root = root.node

        if isinstance(root, cls):
            return True

        if cls._meta.model._meta.proxy:
            model = root._meta.model
        else:
            model = cast(Type[Model], root._meta.model._meta.concrete_model)

        return model == cls._meta.model


class Channel(ModelObjectType):
    id = graphene.GlobalID(required=True)
    name = graphene.String(required=True)
    slug = graphene.String(
        required=True,
    )
    is_active = graphene.Boolean(required=True)

    class Meta:
        model = models.Channel
        interfaces = [graphene.relay.Node]
