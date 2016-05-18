# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pyscada', '0025_auto_20160517_1734'),
    ]

    operations = [
        migrations.CreateModel(
            name='Color',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.SlugField(max_length=80, verbose_name=b'variable name')),
                ('R', models.PositiveSmallIntegerField(default=0)),
                ('G', models.PositiveSmallIntegerField(default=0)),
                ('B', models.PositiveSmallIntegerField(default=0)),
            ],
        ),
        migrations.RemoveField(
            model_name='recordeddataboolean',
            name='time',
        ),
        migrations.RemoveField(
            model_name='recordeddataboolean',
            name='variable',
        ),
        migrations.RemoveField(
            model_name='recordeddatacache',
            name='last_change',
        ),
        migrations.RemoveField(
            model_name='recordeddatacache',
            name='time',
        ),
        migrations.RemoveField(
            model_name='recordeddatacache',
            name='variable',
        ),
        migrations.RemoveField(
            model_name='recordeddatafloat',
            name='time',
        ),
        migrations.RemoveField(
            model_name='recordeddatafloat',
            name='variable',
        ),
        migrations.RemoveField(
            model_name='recordeddataint',
            name='time',
        ),
        migrations.RemoveField(
            model_name='recordeddataint',
            name='variable',
        ),
        migrations.AddField(
            model_name='device',
            name='byte_order',
            field=models.CharField(default=b'1-0-3-2', max_length=15, choices=[(b'1-0-3-2', b'1-0-3-2'), (b'0-1-2-3', b'0-1-2-3'), (b'2-3-0-1', b'2-3-0-1'), (b'3-2-1-0', b'3-2-1-0')]),
        ),
        migrations.AddField(
            model_name='variable',
            name='chart_line_thickness',
            field=models.PositiveSmallIntegerField(default=3, choices=[(3, b'3Px')]),
        ),
        migrations.AddField(
            model_name='variable',
            name='short_name',
            field=models.CharField(default=b'', max_length=80, verbose_name=b'variable short name'),
        ),
        migrations.AlterField(
            model_name='variable',
            name='byte_order',
            field=models.CharField(default=b'default', max_length=15, choices=[(b'default', b'default (specified by device byte order)'), (b'1-0-3-2', b'1-0-3-2'), (b'0-1-2-3', b'0-1-2-3'), (b'2-3-0-1', b'2-3-0-1'), (b'3-2-1-0', b'3-2-1-0')]),
        ),
        migrations.AlterField(
            model_name='variable',
            name='value_class',
            field=models.CharField(default=b'FLOAT64', max_length=15, verbose_name=b'value_class', choices=[(b'FLOAT32', b'REAL (FLOAT32)'), (b'FLOAT32', b'SINGLE (FLOAT32)'), (b'FLOAT32', b'FLOAT32'), (b'UNIXTIMEF32', b'UNIXTIMEF32'), (b'FLOAT64', b'LREAL (FLOAT64)'), (b'FLOAT64', b'FLOAT  (FLOAT64)'), (b'FLOAT64', b'DOUBLE (FLOAT64)'), (b'FLOAT64', b'FLOAT64'), (b'UNIXTIMEF64', b'UNIXTIMEF64'), (b'INT64', b'INT64'), (b'UINT64', b'UINT64'), (b'UNIXTIMEI64', b'UNIXTIMEI64'), (b'UNIXTIMEI32', b'UNIXTIMEI32'), (b'INT32', b'INT32'), (b'UINT32', b'DWORD (UINT32)'), (b'UINT32', b'UINT32'), (b'INT16', b'INT (INT16)'), (b'INT16', b'INT16'), (b'UINT16', b'WORD (UINT16)'), (b'UINT16', b'UINT (UINT16)'), (b'UINT16', b'UINT16'), (b'BOOLEAN', b'BOOL (BOOLEAN)'), (b'BOOLEAN', b'BOOLEAN')]),
        ),
        migrations.DeleteModel(
            name='RecordedDataBoolean',
        ),
        migrations.DeleteModel(
            name='RecordedDataCache',
        ),
        migrations.DeleteModel(
            name='RecordedDataFloat',
        ),
        migrations.DeleteModel(
            name='RecordedDataInt',
        ),
        migrations.DeleteModel(
            name='RecordedTime',
        ),
        migrations.AddField(
            model_name='variable',
            name='chart_line_color',
            field=models.ForeignKey(default=None, blank=True, to='pyscada.Color', null=True),
        ),
    ]
