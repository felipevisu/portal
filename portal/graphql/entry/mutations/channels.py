from collections import defaultdict
from typing import Dict, List

import graphene
from django.core.exceptions import ValidationError
from django.db import transaction

from portal.graphql.channel import ChannelContext
from portal.graphql.core import ResolveInfo

from ....core.permissions import EntryPermissions
from ....entry.models import Entry as EntryModel
from ....entry.models import EntryChannelListing
from ...channel.mutations.base_channel_listing import BaseChannelListingMutation
from ...core.types.base import BaseInputObjectType
from ...core.types.common import EntryChannelListingError, NonNullList
from ..types import Entry


class PublishableChannelListingInput(BaseInputObjectType):
    channel_id = graphene.ID(required=True)
    is_published = graphene.Boolean()
    is_active = graphene.Boolean()


class EntryChannelListingUpdateInput(BaseInputObjectType):
    update_channels = NonNullList(PublishableChannelListingInput, required=False)
    remove_channels = NonNullList(graphene.ID, required=False)


class EntryChannelListingUpdate(BaseChannelListingMutation):
    entry = graphene.Field(Entry)

    class Arguments:
        id = graphene.ID(required=True)
        input = EntryChannelListingUpdateInput(required=True)

    class Meta:
        permissions = (EntryPermissions.MANAGE_ENTRIES,)
        error_type_class = EntryChannelListingError
        error_type_field = "entry_channel_listing_errors"

    @classmethod
    def update_channels(cls, entry: "EntryModel", update_channels: List[Dict]):
        for update_channel in update_channels:
            channel = update_channel["channel"]
            defaults = {}
            for field in ["is_published", "is_active"]:
                if field in update_channel.keys():
                    defaults[field] = update_channel[field]
            EntryChannelListing.objects.update_or_create(
                entry=entry, channel=channel, defaults=defaults
            )

    @classmethod
    def remove_channels(cls, entry: "EntryModel", remove_channels: List[Dict]):
        EntryChannelListing.objects.filter(
            entry=entry, channel_id__in=remove_channels
        ).delete()

    @classmethod
    def save(cls, info: ResolveInfo, entry: "EntryModel", cleaned_input: Dict):
        with transaction.atomic():
            cls.update_channels(entry, cleaned_input.get("update_channels", []))
            cls.remove_channels(entry, cleaned_input.get("remove_channels", []))

    @classmethod
    def perform_mutation(  # type: ignore[override]
        cls, _root, info: ResolveInfo, /, *, id, input
    ):
        entry = cls.get_node_or_error(info, id, only_type=Entry, field="id")
        errors: defaultdict[str, List[ValidationError]] = defaultdict(list)

        cleaned_input = cls.clean_channels(
            info,
            input,
            errors,
            input_source="update_channels",
        )
        if errors:
            raise ValidationError(errors)

        cls.save(info, entry, cleaned_input)
        return EntryChannelListingUpdate(
            entry=ChannelContext(node=entry, channel_slug=None)
        )
