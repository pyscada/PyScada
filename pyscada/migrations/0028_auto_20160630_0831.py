# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pyscada", "0027_auto_20160530_1436"),
    ]

    operations = [
        migrations.AlterField(
            model_name="variable",
            name="short_name",
            field=models.CharField(
                default=b"",
                max_length=80,
                verbose_name="variable short name",
                blank=True,
            ),
        ),
    ]
