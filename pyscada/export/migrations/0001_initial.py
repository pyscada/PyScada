# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pyscada', '0006_auto_20151130_1449'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExportJob',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('label', models.CharField(default='', max_length=400)),
                ('day_time', models.PositiveSmallIntegerField(default=0, help_text='day time wenn the job will start be started', choices=[(0, '0:00'), (1, '1:00'), (2, '2:00'), (3, '3:00'), (4, '4:00'), (5, '5:00'), (6, '6:00'), (7, '7:00'), (8, '8:00'), (9, '9:00'), (10, '10:00'), (11, '11:00'), (12, '12:00'), (13, '13:00'), (14, '14:00'), (15, '15:00'), (16, '16:00'), (17, '17:00'), (18, '18:00'), (19, '19:00'), (20, '20:00'), (21, '21:00'), (22, '22:00'), (23, '23:00')])),
                ('mean_value_period', models.PositiveSmallIntegerField(default=0, help_text='in Seconds (0 = no mean value)')),
                ('active', models.BooleanField(default=False, help_text='to activate scheduled export')),
                ('file_format', models.CharField(default='', max_length=400)),
                ('export_period', models.PositiveSmallIntegerField(default=0, help_text=b'', choices=[(1, '1 Day'), (2, '2 Days (on every even Day of the year)'), (7, '7 Days (on Mondays)'), (14, '14 Days'), (30, '30 Days')])),
                ('variables', models.ManyToManyField(to='pyscada.Variable')),
            ],
        ),
    ]
