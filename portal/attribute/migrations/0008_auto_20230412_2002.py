# Generated by Django 3.2.18 on 2023-04-12 23:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('entry', '0009_entry_active'),
        ('attribute', '0007_alter_attribute_input_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='attributevalue',
            name='date_time',
        ),
        migrations.AddField(
            model_name='attributevalue',
            name='reference_product',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='references', to='entry.entry'),
        ),
    ]
