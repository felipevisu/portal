# Generated by Django 3.2.18 on 2023-04-01 17:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0006_alter_event_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='type',
            field=models.CharField(choices=[('DOCUMENT_CREATE', 'document_create'), ('DOCUMENT_UPDATED', 'document_updated'), ('DOCUMENT_DELETED', 'document_deleted'), ('DOCUMENT_RECEIVED', 'document_received'), ('DOCUMENT_APPROVED', 'document_approved'), ('DOCUMENT_DECLINED', 'document_declined'), ('DOCUMENT_REQUESTED', 'document_requested'), ('ENTRY_CREATED', 'entry_created'), ('ENTRY_UPDATED', 'entry_updated'), ('ENTRY_DELETED', 'entry_deleted')], max_length=255),
        ),
    ]
