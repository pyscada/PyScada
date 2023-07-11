# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pyscada", "0019_datamigration_20160228_1624"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="recordedevent",
            name="time_begin",
        ),
        migrations.RemoveField(
            model_name="recordedevent",
            name="time_end",
        ),
    ]
