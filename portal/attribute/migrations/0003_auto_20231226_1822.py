# Generated by Django 4.2.3 on 2023-12-26 21:22

from django.db import migrations
from django_tenants.utils import schema_context


def create_attribute_entry_objects(apps, schema_editor):
    Attribute = apps.get_model("attribute", "Attribute")
    AttributeEntry = apps.get_model("attribute", "AttributeEntry")
    EntryType = apps.get_model("entry", "EntryType")
    Client = apps.get_model("customer", "Client")

    clients = Client.objects.exclude(schema_name="public")

    for client in clients:
        with schema_context(client.schema_name):
            attributes = Attribute.objects.all()
            vehicle = EntryType.objects.get(slug="veiculo")
            provider = EntryType.objects.get(slug="fornecedor")
            for attribute in attributes:
                if attribute.type == "vehicle":
                    AttributeEntry.objects.create(
                        attribute=attribute, entry_type=vehicle
                    )
                if attribute.type == "provider":
                    AttributeEntry.objects.create(
                        attribute=attribute, entry_type=provider
                    )
                if attribute.type == "vehicle_and_provider":
                    AttributeEntry.objects.create(
                        attribute=attribute, entry_type=provider
                    )
                    AttributeEntry.objects.create(
                        attribute=attribute, entry_type=vehicle
                    )


class Migration(migrations.Migration):
    dependencies = [
        ("attribute", "0002_attributeentry_attribute_entry_types"),
    ]

    operations = [migrations.RunPython(create_attribute_entry_objects)]
