# Generated by Django 3.2.18 on 2023-03-08 22:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entry', '0003_auto_20230203_1639'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entry',
            name='email',
            field=models.CharField(default='', max_length=258),
            preserve_default=False,
        ),
    ]
