# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("export", "0005_auto_20160403_1454"),
    ]

    operations = [
        migrations.AlterField(
            model_name="exporttask",
            name="backgroundtask",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.SET_NULL,
                blank=True,
                to="pyscada.BackgroundTask",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="exporttask",
            name="label",
            field=models.CharField(default="None", max_length=400, blank=True),
        ),
        migrations.AlterField(
            model_name="exporttask",
            name="start",
            field=models.FloatField(default=0, blank=True),
        ),
        migrations.AlterField(
            model_name="exporttask",
            name="time_max",
            field=models.FloatField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name="exporttask",
            name="time_min",
            field=models.FloatField(default=None, null=True),
        ),
    ]
