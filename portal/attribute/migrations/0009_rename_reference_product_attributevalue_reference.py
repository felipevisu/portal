# Generated by Django 3.2.18 on 2023-04-12 23:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('attribute', '0008_auto_20230412_2002'),
    ]

    operations = [
        migrations.RenameField(
            model_name='attributevalue',
            old_name='reference_product',
            new_name='reference',
        ),
    ]