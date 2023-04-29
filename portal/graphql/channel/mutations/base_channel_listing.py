from typing import DefaultDict, Dict, Iterable, List

from django.core.exceptions import ValidationError

from ....channel import models
from ...core import ResolveInfo
from ...core.mutations import BaseMutation
from ...core.utils import get_duplicated_values, get_duplicates_items
from ..types import Channel

ErrorType = DefaultDict[str, List[ValidationError]]


class BaseChannelListingMutation(BaseMutation):
    class Meta:
        abstract = True

    @classmethod
    def validate_duplicated_channel_ids(
        cls,
        add_channels_ids: Iterable[str],
        remove_channels_ids: Iterable[str],
        errors: ErrorType,
    ):
        duplicated_ids = get_duplicates_items(add_channels_ids, remove_channels_ids)
        if duplicated_ids:
            error_msg = (
                "The same object cannot be in both lists "
                "for adding and removing items."
            )
            errors["input"].append(
                ValidationError(error_msg, params={"channels": list(duplicated_ids)})
            )

    @classmethod
    def validate_duplicated_channel_values(
        cls, channels_ids: Iterable[str], field_name: str, errors: ErrorType
    ):
        duplicates = get_duplicated_values(channels_ids)
        if duplicates:
            errors[field_name].append(
                ValidationError(
                    "Duplicated channel ID.", params={"channels": duplicates}
                )
            )

    @classmethod
    def clean_channels(
        cls,
        info: ResolveInfo,
        input,
        errors: ErrorType,
        input_source="add_channels",
    ) -> Dict:
        add_channels = input.get(input_source, [])
        add_channels_ids = [channel["channel_id"] for channel in add_channels]
        remove_channels_ids = input.get("remove_channels", [])
        cls.validate_duplicated_channel_ids(
            add_channels_ids, remove_channels_ids, errors
        )
        cls.validate_duplicated_channel_values(add_channels_ids, input_source, errors)
        cls.validate_duplicated_channel_values(
            remove_channels_ids, "remove_channels", errors
        )

        if errors:
            return {}
        channels_to_add: List["models.Channel"] = []
        if add_channels_ids:
            channels_to_add = cls.get_nodes_or_error(
                add_channels_ids, "channel_id", Channel
            )
        remove_channels_pks = cls.get_global_ids_or_error(
            remove_channels_ids, Channel, field="remove_channels"
        )

        cleaned_input = {input_source: [], "remove_channels": remove_channels_pks}

        for channel_listing, channel in zip(add_channels, channels_to_add):
            channel_listing["channel"] = channel
            cleaned_input[input_source].append(channel_listing)

        return cleaned_input
