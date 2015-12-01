# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hmi', '0004_auto_20151130_1502'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hmivariable',
            name='chart_line_color',
            field=models.ForeignKey(on_delete=models.SET(1), default=1, to='hmi.Color'),
        ),
        migrations.AlterField(
            model_name='widget',
            name='page',
            field=models.ForeignKey(to='hmi.Page'),
        ),
    ]
