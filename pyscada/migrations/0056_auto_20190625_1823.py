# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-06-25 18:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pyscada", "0055_auto_20190625_1752"),
    ]

    operations = [
        migrations.AlterField(
            model_name="backgroundprocess",
            name="pid",
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="event",
            name="hysteresis",
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name="mail",
            name="send_fail_count",
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="mail",
            name="timestamp",
            field=models.FloatField(default=0),
        ),
    ]
