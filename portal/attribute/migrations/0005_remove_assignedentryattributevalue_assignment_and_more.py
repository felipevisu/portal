# Generated by Django 4.2.3 on 2023-12-26 22:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        (
            "attribute",
            "0004_alter_assigneddocumentattributevalue_unique_together_and_more",
        ),
    ]

    operations = [
        migrations.RemoveField(
            model_name="assignedentryattributevalue",
            name="assignment",
        ),
        migrations.RemoveField(
            model_name="attribute",
            name="assigned_entries",
        ),
        migrations.DeleteModel(
            name="AssignedEntryAttribute",
        ),
    ]
