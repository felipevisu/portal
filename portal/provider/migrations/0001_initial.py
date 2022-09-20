# Generated by Django 3.2.12 on 2022-08-10 00:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Segment",
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
                "permissions": (("manage_segments", "Manage segments."),),
            },
        ),
        migrations.CreateModel(
            name="Provider",
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
                ("publication_date", models.DateField(blank=True, null=True)),
                ("is_published", models.BooleanField(default=False)),
                ("document_number", models.CharField(max_length=256)),
                (
                    "segment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="providers",
                        to="provider.segment",
                    ),
                ),
            ],
            options={
                "ordering": ["name"],
                "permissions": (("manage_providers", "Manage providers."),),
            },
        ),
    ]
