# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pyscada", "0020_auto_20160228_1641"),
    ]

    operations = [
        migrations.RenameField(
            model_name="recordedevent",
            old_name="time_begin_new",
            new_name="time_begin",
        ),
        migrations.RenameField(
            model_name="recordedevent",
            old_name="time_end_new",
            new_name="time_end",
        ),
    ]
