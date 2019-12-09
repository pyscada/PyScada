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
                ('name', models.SlugField(max_length=80, verbose_name='variable name')),
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
            field=models.CharField(default='1-0-3-2', max_length=15, choices=[('1-0-3-2', '1-0-3-2'), ('0-1-2-3', '0-1-2-3'), ('2-3-0-1', '2-3-0-1'), ('3-2-1-0', '3-2-1-0')]),
        ),
        migrations.AddField(
            model_name='variable',
            name='chart_line_thickness',
            field=models.PositiveSmallIntegerField(default=3, choices=[(3, '3Px')]),
        ),
        migrations.AddField(
            model_name='variable',
            name='short_name',
            field=models.CharField(default=b'', max_length=80, verbose_name='variable short name'),
        ),
        migrations.AlterField(
            model_name='variable',
            name='byte_order',
            field=models.CharField(default='default', max_length=15, choices=[('default', 'default (specified by device byte order)'), ('1-0-3-2', '1-0-3-2'), ('0-1-2-3', '0-1-2-3'), ('2-3-0-1', '2-3-0-1'), ('3-2-1-0', '3-2-1-0')]),
        ),
        migrations.AlterField(
            model_name='variable',
            name='value_class',
            field=models.CharField(default='FLOAT64', max_length=15, verbose_name='value_class', choices=[('FLOAT32', 'REAL (FLOAT32)'), ('FLOAT32', 'SINGLE (FLOAT32)'), ('FLOAT32', 'FLOAT32'), ('UNIXTIMEF32', 'UNIXTIMEF32'), ('FLOAT64', 'LREAL (FLOAT64)'), ('FLOAT64', 'FLOAT  (FLOAT64)'), ('FLOAT64', 'DOUBLE (FLOAT64)'), ('FLOAT64', 'FLOAT64'), ('UNIXTIMEF64', 'UNIXTIMEF64'), ('INT64', 'INT64'), ('UINT64', 'UINT64'), ('UNIXTIMEI64', 'UNIXTIMEI64'), ('UNIXTIMEI32', 'UNIXTIMEI32'), ('INT32', 'INT32'), ('UINT32', 'DWORD (UINT32)'), ('UINT32', 'UINT32'), ('INT16', 'INT (INT16)'), ('INT16', 'INT16'), ('UINT16', 'WORD (UINT16)'), ('UINT16', 'UINT (UINT16)'), ('UINT16', 'UINT16'), ('BOOLEAN', 'BOOL (BOOLEAN)'), ('BOOLEAN', 'BOOLEAN')]),
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
            field=models.ForeignKey(default=None, blank=True, to='pyscada.Color', null=True, on_delete=models.CASCADE),
        ),
    ]
