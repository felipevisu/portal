# Generated by Django 4.2.3 on 2023-08-30 16:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("channel", "0001_initial"),
        ("investment", "0004_alter_investment_unique_together"),
    ]

    operations = [
        migrations.AlterField(
            model_name="investment",
            name="channel",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="channel.channel"
            ),
        ),
    ]