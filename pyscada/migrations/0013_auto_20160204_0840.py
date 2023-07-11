# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("pyscada", "0012_auto_20160119_0950"),
    ]

    operations = [
        migrations.CreateModel(
            name="Scaling",
            fields=[
                ("id", models.AutoField(serialize=False, primary_key=True)),
                (
                    "description",
                    models.TextField(
                        default=b"", null=True, verbose_name="Description"
                    ),
                ),
                ("input_low", models.FloatField()),
                ("input_high", models.FloatField()),
                ("output_low", models.FloatField()),
                ("output_high", models.FloatField()),
            ],
        ),
        migrations.AddField(
            model_name="variable",
            name="scaling",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.SET_NULL,
                to="pyscada.Scaling",
                null=True,
            ),
        ),
    ]
