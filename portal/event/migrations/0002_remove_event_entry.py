# Generated by Django 3.2.12 on 2023-03-06 21:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("event", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="event",
            name="entry",
        ),
    ]
