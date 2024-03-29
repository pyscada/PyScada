# Generated by Django 2.2.8 on 2020-12-02 14:45

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("hmi", "0046_auto_20201201_2109"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="chartaxis",
            options={"verbose_name": "Y Axis", "verbose_name_plural": "Y Axis"},
        ),
        migrations.AddField(
            model_name="chartaxis",
            name="position",
            field=models.PositiveSmallIntegerField(
                choices=[(0, "left"), (1, "right")], default=0
            ),
        ),
    ]
