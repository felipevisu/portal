# Generated by Django 3.2.18 on 2023-04-13 00:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attribute', '0011_auto_20230412_2040'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attribute',
            name='entity_type',
            field=models.CharField(blank=True, choices=[('vehicle', 'vehicle'), ('provider', 'provider')], max_length=50, null=True),
        ),
    ]