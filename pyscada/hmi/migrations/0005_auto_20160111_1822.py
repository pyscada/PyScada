# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("hmi", "0004_auto_20151130_1502"),
    ]

    operations = [
        migrations.AlterField(
            model_name="processflowdiagramitem",
            name="variable",
            field=models.ForeignKey(
                default=None,
                blank=True,
                to="pyscada.Variable",
                null=True,
                on_delete=models.SET_NULL,
            ),
        ),
    ]
