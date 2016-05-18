# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hmi', '0006_auto_20160111_1848'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chartset',
            name='chart_1',
        ),
        migrations.RemoveField(
            model_name='chartset',
            name='chart_2',
        ),
        migrations.RemoveField(
            model_name='hmivariable',
            name='chart_line_color',
        ),
        migrations.RemoveField(
            model_name='hmivariable',
            name='hmi_variable',
        ),
        migrations.RemoveField(
            model_name='widget',
            name='chart_set',
        ),
        migrations.DeleteModel(
            name='ChartSet',
        ),
        migrations.DeleteModel(
            name='Color',
        ),
        migrations.DeleteModel(
            name='HMIVariable',
        ),
    ]
