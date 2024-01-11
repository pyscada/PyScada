# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ("pyscada", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="event",
            name="hysteresis",
            field=models.FloatField(default=0, blank=True),
            preserve_default=True,
        ),
    ]
