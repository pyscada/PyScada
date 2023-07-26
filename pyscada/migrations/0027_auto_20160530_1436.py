# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pyscada", "0026_auto_20160518_0848"),
    ]

    operations = [
        migrations.CreateModel(
            name="VariableState",
            fields=[],
            options={
                "proxy": True,
            },
            bases=("pyscada.variable",),
        ),
        migrations.AddField(
            model_name="backgroundtask",
            name="restart_daemon",
            field=models.BooleanField(default=False),
        ),
    ]
