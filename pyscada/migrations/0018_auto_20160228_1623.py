# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pyscada", "0017_recordeddata"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="variablechangehistory",
            name="time",
        ),
        migrations.RemoveField(
            model_name="variablechangehistory",
            name="variable",
        ),
        migrations.AddField(
            model_name="recordedevent",
            name="time_begin_new",
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name="recordedevent",
            name="time_end_new",
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.DeleteModel(
            name="VariableChangeHistory",
        ),
    ]
