# Generated by Django 3.2.18 on 2023-04-29 20:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('session', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='session',
            name='publication_date',
        ),
    ]