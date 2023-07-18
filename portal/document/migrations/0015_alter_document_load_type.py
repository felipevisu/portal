# Generated by Django 3.2.18 on 2023-04-19 17:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("document", "0014_alter_document_load_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="document",
            name="load_type",
            field=models.CharField(
                choices=[
                    ("empty", "empty"),
                    ("cnc", "cnc"),
                    ("cndt", "cndt"),
                    ("fgts", "fgts"),
                ],
                default="empty",
                max_length=256,
            ),
        ),
    ]
