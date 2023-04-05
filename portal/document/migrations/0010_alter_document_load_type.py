# Generated by Django 3.2.18 on 2023-04-05 19:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0009_document_load_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='load_type',
            field=models.CharField(choices=[('empty', 'Nenhum'), ('consult_correctional_negative_certificate', 'Certidão Negativa Correcionalo')], default='empty', max_length=256),
        ),
    ]
