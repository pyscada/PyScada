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
                ('label', models.CharField(default=b'', max_length=400)),
                ('day_time', models.PositiveSmallIntegerField(default=0, help_text=b'day time wenn the job will start be started', choices=[(0, b'0:00'), (1, b'1:00'), (2, b'2:00'), (3, b'3:00'), (4, b'4:00'), (5, b'5:00'), (6, b'6:00'), (7, b'7:00'), (8, b'8:00'), (9, b'9:00'), (10, b'10:00'), (11, b'11:00'), (12, b'12:00'), (13, b'13:00'), (14, b'14:00'), (15, b'15:00'), (16, b'16:00'), (17, b'17:00'), (18, b'18:00'), (19, b'19:00'), (20, b'20:00'), (21, b'21:00'), (22, b'22:00'), (23, b'23:00')])),
                ('mean_value_period', models.PositiveSmallIntegerField(default=0, help_text=b'in Seconds (0 = no mean value)')),
                ('active', models.BooleanField(default=False, help_text=b'to activate scheduled export')),
                ('file_format', models.CharField(default=b'', max_length=400)),
                ('export_period', models.PositiveSmallIntegerField(default=0, help_text=b'', choices=[(1, b'1 Day'), (2, b'2 Days (on every even Day of the year)'), (7, b'7 Days (on Mondays)'), (14, b'14 Days'), (30, b'30 Days')])),
                ('variables', models.ManyToManyField(to='pyscada.Variable')),
            ],
        ),
    ]
