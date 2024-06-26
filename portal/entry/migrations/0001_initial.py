# Generated by Django 4.2.10 on 2024-05-01 17:24

import django.core.serializers.json
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("channel", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=256)),
                ("slug", models.SlugField(max_length=256, unique=True)),
            ],
            options={
                "ordering": ["name"],
                "permissions": (("manage_categories", "Manage categories."),),
            },
        ),
        migrations.CreateModel(
            name="EntryType",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=256)),
                ("slug", models.SlugField(max_length=256, unique=True)),
            ],
            options={
                "ordering": ["slug"],
                "permissions": (("manage_entry_types", "Manage entry types."),),
            },
        ),
        migrations.CreateModel(
            name="Entry",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=256)),
                ("slug", models.SlugField(max_length=256, unique=True)),
                ("document_number", models.CharField(max_length=256)),
                ("document_file", models.FileField(blank=True, upload_to="entry")),
                ("email", models.CharField(max_length=258)),
                (
                    "entry_type",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="entries",
                        to="entry.entrytype",
                    ),
                ),
            ],
            options={
                "ordering": ["name"],
                "permissions": (("manage_entries", "Manage entries."),),
            },
        ),
        migrations.CreateModel(
            name="Consult",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
                ("plugin", models.CharField(max_length=64)),
                (
                    "response",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        encoder=django.core.serializers.json.DjangoJSONEncoder,
                    ),
                ),
                (
                    "entry",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="consult",
                        to="entry.entry",
                    ),
                ),
            ],
            options={
                "ordering": ["-created"],
            },
        ),
        migrations.CreateModel(
            name="CategoryEntry",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="categoryentry",
                        to="entry.category",
                    ),
                ),
                (
                    "entry",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="categoryentry",
                        to="entry.entry",
                    ),
                ),
            ],
            options={
                "unique_together": {("category", "entry")},
            },
        ),
        migrations.AddField(
            model_name="category",
            name="entries",
            field=models.ManyToManyField(
                blank=True,
                related_name="categories",
                through="entry.CategoryEntry",
                to="entry.entry",
            ),
        ),
        migrations.CreateModel(
            name="EntryChannelListing",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("is_published", models.BooleanField(default=False)),
                ("is_active", models.BooleanField(default=False)),
                (
                    "channel",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="entry_listings",
                        to="channel.channel",
                    ),
                ),
                (
                    "entry",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="channel_listings",
                        to="entry.entry",
                    ),
                ),
            ],
            options={
                "ordering": ("pk",),
                "unique_together": {("entry", "channel")},
            },
        ),
    ]
