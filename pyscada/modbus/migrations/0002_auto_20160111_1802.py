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
            field=models.PositiveSmallIntegerField(default=0, help_text=b'0 use default'),
        ),
        migrations.AddField(
            model_name='modbusclient',
            name='bytesize',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, b'default'), (5, b'FIVEBITS'), (6, b'SIXBITS'), (7, b'SEVENBITS'), (8, b'EIGHTBITS')]),
        ),
        migrations.AddField(
            model_name='modbusclient',
            name='parity',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, b'default'), (1, b'NONE'), (2, b'EVEN'), (3, b'ODD')]),
        ),
        migrations.AddField(
            model_name='modbusclient',
            name='stopbits',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, b'default'), (1, b'one stopbit'), (2, b'2 stopbits')]),
        ),
        migrations.AddField(
            model_name='modbusclient',
            name='timeout',
            field=models.PositiveSmallIntegerField(default=0, help_text=b'0 use default, else value in seconds'),
        ),
        migrations.AlterField(
            model_name='modbusclient',
            name='protocol',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, b'TCP'), (1, b'UDP'), (2, b'serial ASCII'), (3, b'serial RTU'), (4, b'serial Binary')]),
        ),
    ]
