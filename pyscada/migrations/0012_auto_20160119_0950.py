# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pyscada", "0011_auto_20160115_0920"),
    ]

    operations = [
        migrations.AlterField(
            model_name="recordeddataint",
            name="value",
            field=models.BigIntegerField(),
        ),
    ]
