# Generated by Django 3.2.18 on 2023-03-10 19:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("document", "0007_alter_documentfile_document"),
    ]

    operations = [
        migrations.AlterField(
            model_name="document",
            name="default_file",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="+",
                to="document.documentfile",
            ),
        ),
        migrations.AlterField(
            model_name="documentfile",
            name="document",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="files",
                to="document.document",
            ),
        ),
    ]
