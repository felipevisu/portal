# Generated by Django 4.2.3 on 2023-12-26 18:28

from django.db import migrations
from django_tenants.utils import schema_context

from portal.entry import EntryType as EntryTypeEnum


def migrate_to_entry_type_model(apps, schema_editor):
    EntryType = apps.get_model("entry", "EntryType")
    Entry = apps.get_model("entry", "Entry")
    Client = apps.get_model("customer", "Client")

    clients = Client.objects.exclude(schema_name="public")

    for client in clients:
        with schema_context(client.schema_name):
            vehicle, _ = EntryType.objects.get_or_create(name="Veículo", slug="veiculo")
            provider, _ = EntryType.objects.get_or_create(
                name="Fornecedor", slug="fornecedor"
            )
            entries = Entry.objects.all()

            for entry in entries:
                is_provider = entry.type == EntryTypeEnum.PROVIDER
                entry.entry_type = provider if is_provider else vehicle
                entry.save()


class Migration(migrations.Migration):
    dependencies = [
        ("entry", "0002_entrytype_entry_entry_type"),
    ]

    operations = [migrations.RunPython(migrate_to_entry_type_model)]
