# Generated by Django 3.2.12 on 2023-02-27 20:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='document',
            name='begin_date',
        ),
        migrations.RemoveField(
            model_name='document',
            name='expiration_date',
        ),
        migrations.RemoveField(
            model_name='document',
            name='file',
        ),
        migrations.CreateModel(
            name='DocumentFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('file', models.FileField(upload_to='documents')),
                ('begin_date', models.DateField(blank=True, null=True)),
                ('expiration_date', models.DateField(blank=True, null=True)),
                ('document', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='document.document')),
            ],
            options={
                'ordering': ['-created'],
                'permissions': (('manage_documents', 'Manage documents.'),),
            },
        ),
        migrations.AddField(
            model_name='document',
            name='default_file',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='document.documentfile'),
        ),
    ]