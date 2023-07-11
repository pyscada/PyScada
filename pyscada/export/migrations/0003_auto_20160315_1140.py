# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("export", "0002_auto_20151201_1617"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="ExportJob",
            new_name="ScheduledExportTask",
        ),
    ]
