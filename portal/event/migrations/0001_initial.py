# Generated by Django 3.2.12 on 2023-03-06 21:29

from django.conf import settings
import django.core.serializers.json
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('entry', '0003_auto_20230203_1639'),
        ('document', '0003_alter_documentfile_document'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('type', models.CharField(choices=[('DOCUMENT_UPDATED_BY_PROVIDER', 'document_updated_by_provider'), ('DOCUMENT_UPDATED_BY_STAFF', 'document_updated_by_staff'), ('PROVIDER_NOTIFIED_ABOUT_EXPIRED_DOCUMENT', 'provider_notified_about_expired_document'), ('NEW_DOCUMENT_REQUESTED_BY_STAFF', 'new_document_requested_by_staff')], max_length=255)),
                ('parameters', models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder)),
                ('document', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='events', to='document.document')),
                ('entry', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='events', to='entry.entry')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('date',),
            },
        ),
    ]