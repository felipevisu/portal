
from collections import defaultdict

import graphene
from django.forms import ValidationError

from ...core.permissions import InvestmentPermissions
from ...investment import models
from ..core.mutations import BaseMutation, ModelDeleteMutation, ModelMutation
from ..core.types import Error
from .types import Investment, Item


class InvestmentInput(graphene.InputObjectType):
    mounth = graphene.Int()
    year = graphene.Int()
    is_published = graphene.Boolean()


class InvestmentCreate(ModelMutation):
    investment = graphene.Field(Investment)

    class Arguments:
        input = InvestmentInput(required=True)

    class Meta:
        model = models.Investment
        permissions = (InvestmentPermissions.MANAGE_INVESTMENTS,)


class InvestmentUpdate(ModelMutation):
    document = graphene.Field(Investment)

    class Arguments:
        id = graphene.ID()
        input = InvestmentInput(required=True)

    class Meta:
        model = models.Investment
        permissions = (InvestmentPermissions.MANAGE_INVESTMENTS,)


class InvestmentDelete(ModelDeleteMutation):

    class Arguments:
        id = graphene.ID()

    class Meta:
        model = models.Investment
        permissions = (InvestmentPermissions.MANAGE_INVESTMENTS,)


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
        input = ItemInput(required=True)

    class Meta:
        model = models.Investment
        permissions = (InvestmentPermissions.MANAGE_ITEMS,)


class ItemUpdate(ModelMutation):
    item = graphene.Field(Item)

    class Arguments:
        id = graphene.ID()
        input = ItemInput(required=True)

    class Meta:
        model = models.Item
        permissions = (InvestmentPermissions.MANAGE_ITEMS,)


class ItemDelete(ModelDeleteMutation):

    class Arguments:
        id = graphene.ID()

    class Meta:
        model = models.Item
        permissions = (InvestmentPermissions.MANAGE_ITEMS,)


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
        for index, item_data in enumerate(items):
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
            raise ValidationError(errors)  # type: ignore

        for instance in instances:
            instance.save()

        return ItemBulkCreate(items=instances)
