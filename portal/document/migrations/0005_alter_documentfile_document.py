# Generated by Django 3.2.18 on 2023-03-09 02:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0004_alter_documentfile_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documentfile',
            name='document',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='document.document'),
        ),
    ]