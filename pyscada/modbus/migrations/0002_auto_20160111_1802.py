# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('modbus', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='modbusclient',
            name='baudrate',
            field=models.PositiveSmallIntegerField(default=0, help_text='0 use default'),
        ),
        migrations.AddField(
            model_name='modbusclient',
            name='bytesize',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, 'default'), (5, 'FIVEBITS'), (6, 'SIXBITS'), (7, 'SEVENBITS'), (8, 'EIGHTBITS')]),
        ),
        migrations.AddField(
            model_name='modbusclient',
            name='parity',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, 'default'), (1, 'NONE'), (2, 'EVEN'), (3, 'ODD')]),
        ),
        migrations.AddField(
            model_name='modbusclient',
            name='stopbits',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, 'default'), (1, 'one stopbit'), (2, '2 stopbits')]),
        ),
        migrations.AddField(
            model_name='modbusclient',
            name='timeout',
            field=models.PositiveSmallIntegerField(default=0, help_text='0 use default, else value in seconds'),
        ),
        migrations.AlterField(
            model_name='modbusclient',
            name='protocol',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, 'TCP'), (1, 'UDP'), (2, 'serial ASCII'), (3, 'serial RTU'), (4, 'serial Binary')]),
        ),
    ]
