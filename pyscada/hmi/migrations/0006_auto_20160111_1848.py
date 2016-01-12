# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hmi', '0005_auto_20160111_1822'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hmivariable',
            name='chart_line_color',
            field=models.ForeignKey(default=None, blank=True, to='hmi.Color', null=True),
        ),
        migrations.AlterField(
            model_name='widget',
            name='page',
            field=models.ForeignKey(default=None, blank=True, to='hmi.Page', null=True),
        ),
    ]
