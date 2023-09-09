# Generated by Django 4.2.3 on 2023-09-09 16:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("entry", "0001_initial"),
        ("document", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="AssignedDocumentAttribute",
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
            ],
        ),
        migrations.CreateModel(
            name="AssignedEntryAttribute",
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
            ],
        ),
        migrations.CreateModel(
            name="Attribute",
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
                    "slug",
                    models.SlugField(allow_unicode=True, max_length=250, unique=True),
                ),
                ("name", models.CharField(max_length=255)),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("document", "document"),
                            ("vehicle", "vehicle"),
                            ("provider", "provider"),
                            ("vehicle_and_provider", "vehicle and provider"),
                        ],
                        max_length=50,
                    ),
                ),
                (
                    "input_type",
                    models.CharField(
                        choices=[
                            ("dropdown", "Dropdown"),
                            ("multiselect", "Multi Select"),
                            ("file", "File"),
                            ("plain-text", "Plain Text"),
                            ("swatch", "Swatch"),
                            ("boolean", "Boolean"),
                            ("date", "Date"),
                            ("reference", "Referência"),
                        ],
                        default="dropdown",
                        max_length=50,
                    ),
                ),
                (
                    "entity_type",
                    models.CharField(
                        blank=True,
                        choices=[("vehicle", "vehicle"), ("provider", "provider")],
                        max_length=50,
                        null=True,
                    ),
                ),
                ("value_required", models.BooleanField(blank=True, default=False)),
                ("visible_in_website", models.BooleanField(blank=True, default=True)),
                (
                    "filterable_in_website",
                    models.BooleanField(blank=True, default=False),
                ),
                (
                    "filterable_in_dashboard",
                    models.BooleanField(blank=True, default=False),
                ),
                ("website_search_position", models.IntegerField(blank=True, default=0)),
                ("available_in_grid", models.BooleanField(blank=True, default=False)),
                (
                    "assigned_documents",
                    models.ManyToManyField(
                        blank=True,
                        related_name="attributesrelated",
                        through="attribute.AssignedDocumentAttribute",
                        to="document.document",
                    ),
                ),
                (
                    "assigned_entries",
                    models.ManyToManyField(
                        blank=True,
                        related_name="attributesrelated",
                        through="attribute.AssignedEntryAttribute",
                        to="entry.entry",
                    ),
                ),
            ],
            options={
                "ordering": ("name",),
                "permissions": (("manage_attributes", "Manage attributes."),),
            },
        ),
        migrations.CreateModel(
            name="AttributeValue",
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
                    "sort_order",
                    models.IntegerField(db_index=True, editable=False, null=True),
                ),
                ("name", models.CharField(max_length=250)),
                ("value", models.CharField(blank=True, default="", max_length=100)),
                ("slug", models.SlugField(allow_unicode=True, max_length=255)),
                ("file_url", models.URLField(blank=True, null=True)),
                (
                    "content_type",
                    models.CharField(blank=True, max_length=50, null=True),
                ),
                ("plain_text", models.TextField(blank=True, null=True)),
                ("boolean", models.BooleanField(blank=True, null=True)),
                ("date_time", models.DateTimeField(blank=True, null=True)),
                (
                    "attribute",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="values",
                        to="attribute.attribute",
                    ),
                ),
                (
                    "reference",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="references",
                        to="entry.entry",
                    ),
                ),
            ],
            options={
                "ordering": ("name",),
                "unique_together": {("slug", "attribute")},
            },
        ),
        migrations.CreateModel(
            name="AssignedEntryAttributeValue",
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
                    "assignment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="entryvalueassignment",
                        to="attribute.assignedentryattribute",
                    ),
                ),
                (
                    "value",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="entryvalueassignment",
                        to="attribute.attributevalue",
                    ),
                ),
            ],
            options={
                "ordering": ("pk",),
                "unique_together": {("value", "assignment")},
            },
        ),
        migrations.AddField(
            model_name="assignedentryattribute",
            name="attribute",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="entryassignments",
                to="attribute.attribute",
            ),
        ),
        migrations.AddField(
            model_name="assignedentryattribute",
            name="entry",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="attributes",
                to="entry.entry",
            ),
        ),
        migrations.AddField(
            model_name="assignedentryattribute",
            name="values",
            field=models.ManyToManyField(
                blank=True,
                related_name="entryassignments",
                through="attribute.AssignedEntryAttributeValue",
                to="attribute.attributevalue",
            ),
        ),
        migrations.CreateModel(
            name="AssignedDocumentAttributeValue",
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
                    "assignment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="documentvalueassignment",
                        to="attribute.assigneddocumentattribute",
                    ),
                ),
                (
                    "value",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="documentvalueassignment",
                        to="attribute.attributevalue",
                    ),
                ),
            ],
            options={
                "ordering": ("pk",),
                "unique_together": {("value", "assignment")},
            },
        ),
        migrations.AddField(
            model_name="assigneddocumentattribute",
            name="attribute",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="documentassignments",
                to="attribute.attribute",
            ),
        ),
        migrations.AddField(
            model_name="assigneddocumentattribute",
            name="document",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="attributes",
                to="document.document",
            ),
        ),
        migrations.AddField(
            model_name="assigneddocumentattribute",
            name="values",
            field=models.ManyToManyField(
                blank=True,
                related_name="documentassignments",
                through="attribute.AssignedDocumentAttributeValue",
                to="attribute.attributevalue",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="assignedentryattribute",
            unique_together={("entry", "attribute")},
        ),
        migrations.AlterUniqueTogether(
            name="assigneddocumentattribute",
            unique_together={("document", "attribute")},
        ),
    ]
