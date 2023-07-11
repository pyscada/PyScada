# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("pyscada", "0013_auto_20160204_0840"),
    ]

    operations = [
        migrations.AlterField(
            model_name="scaling",
            name="description",
            field=models.TextField(
                default=b"", null=True, verbose_name="Description", blank=True
            ),
        ),
        migrations.AlterField(
            model_name="variable",
            name="scaling",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.SET_NULL,
                blank=True,
                to="pyscada.Scaling",
                null=True,
            ),
        ),
    ]
