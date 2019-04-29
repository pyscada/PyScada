# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pyscada', '0024_auto_20160517_1047'),
    ]

    operations = [
        migrations.AddField(
            model_name='variable',
            name='byte_order',
            field=models.CharField(default='1-0-3-2', max_length=15, choices=[('1-0-3-2', '1-0-3-2'), ('0-1-2-3', '0-1-2-3'), ('2-3-0-1', '2-3-0-1'), ('3-2-1-0', '3-2-1-0')]),
        ),
        migrations.AlterField(
            model_name='variable',
            name='value_class',
            field=models.CharField(default='FLOAT64', max_length=15, verbose_name='value_class', choices=[('FLOAT32', 'REAL'), ('FLOAT32', 'SINGLE'), ('FLOAT32', 'FLOAT32'), ('UNIXTIMEF32', 'UNIXTIMEF32'), ('FLOAT64', 'LREAL'), ('FLOAT64', 'FLOAT'), ('FLOAT64', 'DOUBLE'), ('FLOAT64', 'FLOAT64'), ('UNIXTIMEF64', 'UNIXTIMEF64'), ('INT64', 'INT64'), ('UINT64', 'UINT64'), ('UNIXTIMEI64', 'UNIXTIMEI64'), ('UNIXTIMEI32', 'UNIXTIMEI32'), ('INT32', 'INT32'), ('UINT32', 'DWORD'), ('UINT32', 'UINT32'), ('INT16', 'INT'), ('INT16', 'INT16'), ('UINT16', 'WORD'), ('UINT16', 'UINT'), ('UINT16', 'UINT16'), ('BOOLEAN', 'BOOL'), ('BOOLEAN', 'BOOLEAN')]),
        ),
    ]
