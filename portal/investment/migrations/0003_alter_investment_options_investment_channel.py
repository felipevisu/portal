# Generated by Django 4.2.3 on 2023-08-15 00:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("channel", "0001_initial"),
        ("investment", "0002_remove_investment_publication_date"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="investment",
            options={
                "ordering": ["-created"],
                "permissions": (("manage_investments", "Manage investments."),),
            },
        ),
        migrations.AddField(
            model_name="investment",
            name="channel",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="channel.channel",
            ),
        ),
    ]
