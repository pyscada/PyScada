# Generated by Django 2.2.24 on 2021-11-15 15:21

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pyscada", "0084_auto_20211115_1503"),
    ]

    operations = [
        migrations.AddField(
            model_name="calculatedvariableselector",
            name="active",
            field=models.BooleanField(default=True),
        ),
    ]
