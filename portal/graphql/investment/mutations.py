from collections import defaultdict

import graphene
from django.core.exceptions import ValidationError

from ...core.permissions import InvestmentPermissions
from ...investment import models
from ..channel.types import Channel
from ..core.mutations import (
    BaseMutation,
    ModelBulkDeleteMutation,
    ModelDeleteMutation,
    ModelMutation,
)
from ..core.types import Error, NonNullList
from .types import Investment, Item


class ItemCreateInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    value = graphene.Float(required=True)


class InvestmentInput(graphene.InputObjectType):
    month = graphene.Int()
    year = graphene.Int()
    is_published = graphene.Boolean()
    channel = graphene.ID()
    items = NonNullList(ItemCreateInput)


class InvestmentUpdateInput(graphene.InputObjectType):
    month = graphene.Int()
    year = graphene.Int()
    is_published = graphene.Boolean()
    channel = graphene.ID()
    add_items = NonNullList(ItemCreateInput)
    remove_items = NonNullList(graphene.ID)


class ItemsMixin:
    INVESTMENT_ITEMS_FIELD = None

    @classmethod
    def clean_items(cls, cleaned_input, investment):
        items_input = cleaned_input.get(cls.INVESTMENT_ITEMS_FIELD)
        if items_input is None:
            return

        for item_data in items_input:
            cls.validate_item(investment, item_data)

    @classmethod
    def validate_item(cls, investment, item_data: dict):
        item = models.Item(**item_data, investment=investment)
        try:
            item.full_clean()
        except ValidationError as validation_errors:
            for field, err in validation_errors.error_dict.items():
                if field == "investment":
                    continue
                raise ValidationError({cls.INVESTMENT_ITEMS_FIELD: err})

    @classmethod
    def _save_m2m(cls, info, investment, cleaned_data):
        super()._save_m2m(info, investment, cleaned_data)
        items = cleaned_data.get(cls.INVESTMENT_ITEMS_FIELD) or []
        for item in items:
            investment.items.create(**item)


class InvestmentCreate(ItemsMixin, ModelMutation):
    INVESTMENT_ITEMS_FIELD = "items"
    investment = graphene.Field(Investment)

    class Arguments:
        input = InvestmentInput(required=True)

    class Meta:
        model = models.Investment
        permissions = (InvestmentPermissions.MANAGE_INVESTMENTS,)
        object_type = Investment

    @classmethod
    def perform_mutation(cls, _root, info, **data):
        input = data.get("input")

        instance = models.Investment()

        cleaned_input = cls.clean_input(info, instance, input)
        cls.clean_items(cleaned_input, instance)

        instance = cls.construct_instance(instance, cleaned_input)
        cls.clean_instance(info, instance)

        instance.save()
        cls._save_m2m(info, instance, cleaned_input)

        return InvestmentCreate(investment=instance)


class InvestmentUpdate(ItemsMixin, ModelMutation):
    INVESTMENT_ITEMS_FIELD = "add_items"
    investment = graphene.Field(Investment)

    class Arguments:
        id = graphene.ID()
        input = InvestmentUpdateInput(required=True)

    class Meta:
        model = models.Investment
        permissions = (InvestmentPermissions.MANAGE_INVESTMENTS,)
        object_type = Investment

    @classmethod
    def clean_remove_items(cls, cleaned_input, instance):
        remove_items = cleaned_input.get("remove_items", [])
        for item in remove_items:
            if item.attribute != instance:
                msg = "Value %s does not belong to this attribute." % item
                raise ValidationError({"remove_values": ValidationError(msg)})
        return remove_items

    @classmethod
    def _save_m2m(cls, info, instance, cleaned_data):
        super()._save_m2m(info, instance, cleaned_data)
        for item in cleaned_data.get("remove_items", []):
            item.delete()

    @classmethod
    def perform_mutation(cls, _root, info, id, input):
        instance = cls.get_node_or_error(info, id, only_type=Investment)

        cleaned_input = cls.clean_input(info, instance, input)
        cls.clean_items(cleaned_input, instance)
        cls.clean_remove_items(cleaned_input, instance)

        instance = cls.construct_instance(instance, cleaned_input)
        cls.clean_instance(info, instance)

        instance.save()
        cls._save_m2m(info, instance, cleaned_input)
        return InvestmentUpdate(investment=instance)


class InvestmentDelete(ModelDeleteMutation):
    class Arguments:
        id = graphene.ID()

    class Meta:
        model = models.Investment
        permissions = (InvestmentPermissions.MANAGE_INVESTMENTS,)
        object_type = Investment


class ItemInput(graphene.InputObjectType):
    name = graphene.String()
    value = graphene.Float()
    investment = graphene.ID()


class ItemBulkInput(graphene.InputObjectType):
    name = graphene.String()
    value = graphene.Float()


class ItemCreate(ModelMutation):
    item = graphene.Field(Item)

    class Arguments:
        investment_id = graphene.ID(required=True)
        input = ItemInput(required=True)

    class Meta:
        model = models.Investment
        permissions = (InvestmentPermissions.MANAGE_ITEMS,)
        object_type = Item

    @classmethod
    def perform_mutation(cls, _root, info, investment_id, input):
        investment = cls.get_node_or_error(info, investment_id, only_type=Investment)
        instance = models.Item(investment=investment)
        cleaned_input = cls.clean_input(info, instance, input)
        instance = cls.construct_instance(instance, cleaned_input)
        cls.clean_instance(info, instance)
        instance.save()
        cls._save_m2m(info, instance, cleaned_input)
        return ItemCreate(item=instance)


class ItemUpdate(ModelMutation):
    item = graphene.Field(Item)

    class Arguments:
        id = graphene.ID()
        input = ItemInput(required=True)

    class Meta:
        model = models.Item
        permissions = (InvestmentPermissions.MANAGE_ITEMS,)
        object_type = Item


class InvestmentBulkDelete(ModelBulkDeleteMutation):
    class Arguments:
        ids = NonNullList(
            graphene.ID, required=True, description="List of segments IDs to delete."
        )

    class Meta:
        description = "Deletes segments."
        model = models.Investment
        object_type = Investment
        permissions = (InvestmentPermissions.MANAGE_ITEMS,)


class ItemDelete(ModelDeleteMutation):
    class Arguments:
        id = graphene.ID()

    class Meta:
        model = models.Item
        permissions = (InvestmentPermissions.MANAGE_ITEMS,)
        object_type = Item


class BulkItemError(Error):
    index = graphene.Int(
        description="Index of an input list item that caused the error."
    )


class ItemBulkCreate(BaseMutation):
    items = graphene.List(Item)

    class Arguments:
        items = graphene.List(ItemBulkInput, required=True)
        investment_id = graphene.ID()

    class Meta:
        permissions = (InvestmentPermissions.MANAGE_ITEMS,)
        error_type_class = BulkItemError

    @classmethod
    def add_indexes_to_errors(cls, index, error, error_dict):
        for key, value in error.error_dict.items():
            for e in value:
                if e.params:
                    e.params["index"] = index
                else:
                    e.params = {"index": index}
            error_dict[key].extend(value)

    @classmethod
    def create_items(cls, info, cleaned_inputs, investment, errors):
        instances = []
        for index, cleaned_input in enumerate(cleaned_inputs):
            if not cleaned_input:
                continue
            try:
                instance = models.Item()
                cleaned_input["investment"] = investment
                instance = cls.construct_instance(instance, cleaned_input)
                cls.clean_instance(info, instance)
                instances.append(instance)
            except ValidationError as exc:
                cls.add_indexes_to_errors(index, exc, errors)
        return instances

    @classmethod
    def clean_item_input(cls, info, instance, data):
        cleaned_input = ModelMutation.clean_input(
            info, instance, data, input_cls=ItemBulkInput
        )
        return cleaned_input

    @classmethod
    def clean_items(cls, info, items, investment):
        cleaned_inputs = []
        for _, item_data in enumerate(items):
            item_data["investment"] = investment
            cleaned_input = cls.clean_item_input(info, None, item_data)
            cleaned_inputs.append(cleaned_input if cleaned_input else None)

        return cleaned_inputs

    @classmethod
    def perform_mutation(cls, root, info, **data):
        investment = cls.get_node_or_error(info, data["investment_id"])
        errors = defaultdict(list)

        cleaned_inputs = cls.clean_items(info, data["items"], investment)
        instances = cls.create_items(info, cleaned_inputs, investment, errors)

        if errors:
            raise ValidationError(errors)

        for instance in instances:
            instance.save()

        return ItemBulkCreate(items=instances)
