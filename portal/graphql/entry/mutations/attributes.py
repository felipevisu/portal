from collections import defaultdict

import graphene
from django.core.exceptions import ValidationError
from django.db.models import Q

from portal.attribute import AttributeType
from portal.attribute import models as attribute_models
from portal.core.permissions import EntryPermissions
from portal.entry import models
from portal.graphql.attribute.types import Attribute
from portal.graphql.core import ResolveInfo
from portal.graphql.core.mutations import BaseMutation
from portal.graphql.core.types.common import EntryError, NonNullList
from portal.graphql.entry.types.entries import EntryType

from ...core.types.base import BaseInputObjectType


class EntryAttributeAssignInput(BaseInputObjectType):
    id = graphene.ID(required=True, description="The ID of the attribute to assign.")


class EntryAttributeAssignmentUpdateInput(BaseInputObjectType):
    id = graphene.ID(required=True, description="The ID of the attribute to assign.")


class EntryAttributeAssign(BaseMutation):
    entry_type = graphene.Field(EntryType, description="The updated entry type.")

    class Arguments:
        entry_type_id = graphene.ID(
            required=True,
            description="ID of the entry type to assign the attributes into.",
        )
        operations = NonNullList(
            EntryAttributeAssignInput,
            required=True,
            description="The operations to perform.",
        )

    class Meta:
        description = "Assign attributes to a given entry type."
        error_type_class = EntryError
        error_type_field = "entry_errors"
        permissions = (EntryPermissions.MANAGE_ENTRY_TYPES,)

    @classmethod
    def get_operations(
        cls, info: ResolveInfo, operations: list[EntryAttributeAssignInput]
    ):
        """Resolve all passed global ids into integer PKs of the Attribute type."""
        entry_attrs_pks = []
        for operation in operations:
            pk = cls.get_global_id_or_error(
                operation.id, only_type=Attribute, field="operations"
            )
            entry_attrs_pks.append(pk)
        return entry_attrs_pks

    @classmethod
    def check_attributes_types(cls, errors, entry_attrs_pks):
        """Ensure the attributes are entry attributes."""

        not_valid_attributes = attribute_models.Attribute.objects.filter(
            pk__in=entry_attrs_pks
        ).exclude(type=AttributeType.ENTRY_TYPE)

        if not_valid_attributes:
            not_valid_attr_ids = [
                graphene.Node.to_global_id("Attribute", attr.pk)
                for attr in not_valid_attributes
            ]
            error = ValidationError(
                "Only entry attributes can be assigned.",
                params={"attributes": not_valid_attr_ids},
            )
            errors["operations"].append(error)

    @classmethod
    def check_operations_not_assigned_already(cls, errors, entry_type, entry_attrs_pks):
        qs = (
            attribute_models.Attribute.objects.get_assigned_entry_type_attributes(
                entry_type.pk
            )
            .values_list("pk", "name", "slug")
            .filter(pk__in=entry_attrs_pks)
        )

        invalid_attributes = list(qs)
        if invalid_attributes:
            msg = ", ".join(
                [f"{name} ({slug})" for _, name, slug in invalid_attributes]
            )
            invalid_attr_ids = [
                graphene.Node.to_global_id("Attribute", attr[0])
                for attr in invalid_attributes
            ]
            error = ValidationError(
                (f"{msg} have already been assigned to this entry type."),
                params={"attributes": invalid_attr_ids},
            )
            errors["operations"].append(error)

    @classmethod
    def clean_operations(cls, entry_type, entry_attrs_data):
        """Ensure the attributes are not already assigned to the entry type."""
        errors = defaultdict(list)
        entry_attrs_pks = entry_attrs_data
        attributes = attribute_models.Attribute.objects.filter(
            id__in=entry_attrs_pks
        ).values_list("pk", flat=True)
        if len(entry_attrs_pks) != len(attributes):
            invalid_attrs = set(entry_attrs_pks) - set(attributes)
            invalid_attrs = [
                graphene.Node.to_global_id("Attribute", pk) for pk in invalid_attrs
            ]
            error = ValidationError(
                "Attribute doesn't exist.",
                params={"attributes": list(invalid_attrs)},
            )
            errors["operations"].append(error)

        cls.check_attributes_types(errors, entry_attrs_pks)
        cls.check_operations_not_assigned_already(errors, entry_type, entry_attrs_pks)

        if errors:
            raise ValidationError(errors)

    @classmethod
    def save_field_values(cls, entry_type, pks):
        for pk in pks:
            attribute_models.AttributeEntry.objects.create(
                entry_type=entry_type,
                attribute_id=pk,
            )

    @classmethod
    def perform_mutation(cls, _root, info: ResolveInfo, /, **data):
        entry_type_id: str = data["entry_type_id"]
        operations: list[EntryAttributeAssignInput] = data["operations"]
        entry_type: models.EntryType = graphene.Node.get_node_from_global_id(
            info, entry_type_id, only_type=EntryType
        )
        entry_attrs_data = cls.get_operations(info, operations)

        cls.clean_operations(entry_type, entry_attrs_data)
        cls.save_field_values(entry_type, entry_attrs_data)

        return cls(entry_type=entry_type)


class EntryAttributeUnassign(BaseMutation):
    entry_type = graphene.Field(EntryType, description="The updated entry type.")

    class Arguments:
        entry_type_id = graphene.ID(
            required=True,
            description=(
                "ID of the entry type from which the attributes should be unassigned."
            ),
        )
        attribute_ids = NonNullList(
            graphene.ID,
            required=True,
            description="The IDs of the attributes to unassign.",
        )

    class Meta:
        description = "Un-assign attributes from a given entry type."
        error_type_class = EntryError
        error_type_field = "entry_errors"
        permissions = (EntryPermissions.MANAGE_ENTRY_TYPES,)

    @classmethod
    def save_field_values(cls, product_type, field, pks):
        """Add in bulk the PKs to assign to a given entry type."""
        getattr(product_type, field).remove(*pks)

    @classmethod
    def perform_mutation(cls, _root, info: ResolveInfo, /, **data):
        entry_type_id: str = data["entry_type_id"]
        attribute_ids: list[str] = data["attribute_ids"]
        # Retrieve the requested entry type
        entry_type = graphene.Node.get_node_from_global_id(
            info, entry_type_id, only_type=EntryType
        )  # type: models.ProductType

        # Resolve all the passed IDs to ints
        attribute_pks = [
            cls.get_global_id_or_error(
                attribute_id, only_type=Attribute, field="attribute_id"
            )
            for attribute_id in attribute_ids
        ]

        # Commit
        cls.save_field_values(entry_type, "entry_attributes", attribute_pks)

        return cls(entry_type=entry_type)
