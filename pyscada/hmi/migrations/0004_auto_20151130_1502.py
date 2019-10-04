# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hmi', '0003_auto_20151130_1456'),
    ]

    operations = [
        migrations.AlterField(
            model_name='controlitem',
            name='variable',
            field=models.ForeignKey(to='pyscada.Variable', null=True, on_delete=models.SET_NULL),
        ),
        # migrations.AlterField(
        #     model_name='hmivariable',
        #     name='chart_line_color',
        #     field=models.ForeignKey(on_delete=models.SET(1), default=1, to='hmi.Color', null=True),
        # ),
        # migrations.AlterField(
        #     model_name='widget',
        #     name='page',
        #     field=models.ForeignKey(default=1, to='hmi.Page'),
        #     preserve_default=False,
        # ),
    ]
