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
            field=models.CharField(default=b'1-0-3-2', max_length=15, choices=[(b'1-0-3-2', b'1-0-3-2'), (b'0-1-2-3', b'0-1-2-3'), (b'2-3-0-1', b'2-3-0-1'), (b'3-2-1-0', b'3-2-1-0')]),
        ),
        migrations.AlterField(
            model_name='variable',
            name='value_class',
            field=models.CharField(default=b'FLOAT64', max_length=15, verbose_name=b'value_class', choices=[(b'FLOAT32', b'REAL'), (b'FLOAT32', b'SINGLE'), (b'FLOAT32', b'FLOAT32'), (b'UNIXTIMEF32', b'UNIXTIMEF32'), (b'FLOAT64', b'LREAL'), (b'FLOAT64', b'FLOAT'), (b'FLOAT64', b'DOUBLE'), (b'FLOAT64', b'FLOAT64'), (b'UNIXTIMEF64', b'UNIXTIMEF64'), (b'INT64', b'INT64'), (b'UINT64', b'UINT64'), (b'UNIXTIMEI64', b'UNIXTIMEI64'), (b'UNIXTIMEI32', b'UNIXTIMEI32'), (b'INT32', b'INT32'), (b'UINT32', b'DWORD'), (b'UINT32', b'UINT32'), (b'INT16', b'INT'), (b'INT16', b'INT16'), (b'UINT16', b'WORD'), (b'UINT16', b'UINT'), (b'UINT16', b'UINT16'), (b'BOOLEAN', b'BOOL'), (b'BOOLEAN', b'BOOLEAN')]),
        ),
    ]
