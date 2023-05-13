# Generated by Django 3.2.18 on 2023-05-13 16:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0010_auto_20230419_1743'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='document_name',
            field=models.CharField(blank=True, max_length=512, null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='user_email',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
    ]
