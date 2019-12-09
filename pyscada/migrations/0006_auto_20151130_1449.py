# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pyscada', '0005_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clientwritetask',
            name='variable',
            field=models.ForeignKey(default=1, to='pyscada.Variable', on_delete=models.CASCADE),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='event',
            name='variable',
            field=models.ForeignKey(default=1, to='pyscada.Variable', on_delete=models.CASCADE),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='recordeddataboolean',
            name='time',
            field=models.ForeignKey(default=1, to='pyscada.RecordedTime', on_delete=models.CASCADE),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='recordeddataboolean',
            name='variable',
            field=models.ForeignKey(default=1, to='pyscada.Variable', on_delete=models.CASCADE),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='recordeddatacache',
            name='last_change',
            field=models.ForeignKey(related_name='last_change', default=1, to='pyscada.RecordedTime',
                                    on_delete=models.CASCADE),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='recordeddatacache',
            name='time',
            field=models.ForeignKey(default=1, to='pyscada.RecordedTime', on_delete=models.CASCADE),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='recordeddatacache',
            name='variable',
            field=models.OneToOneField(default=1, to='pyscada.Variable', on_delete=models.CASCADE),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='recordeddatafloat',
            name='time',
            field=models.ForeignKey(default=1, to='pyscada.RecordedTime', on_delete=models.CASCADE),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='recordeddatafloat',
            name='variable',
            field=models.ForeignKey(default=1, to='pyscada.Variable', on_delete=models.CASCADE),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='recordeddataint',
            name='time',
            field=models.ForeignKey(default=1, to='pyscada.RecordedTime', on_delete=models.CASCADE),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='recordeddataint',
            name='variable',
            field=models.ForeignKey(default=1, to='pyscada.Variable', on_delete=models.CASCADE),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='recordedevent',
            name='event',
            field=models.ForeignKey(default=1, to='pyscada.Event', on_delete=models.CASCADE),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='recordedevent',
            name='time_begin',
            field=models.ForeignKey(default=1, to='pyscada.RecordedTime', on_delete=models.CASCADE),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='variable',
            name='client',
            field=models.ForeignKey(default=1, to='pyscada.Client', on_delete=models.CASCADE),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='variable',
            name='unit',
            field=models.ForeignKey(on_delete=models.SET(1), default=1, to='pyscada.Unit'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='variablechangehistory',
            name='time',
            field=models.ForeignKey(default=1, to='pyscada.RecordedTime', on_delete=models.CASCADE),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='variablechangehistory',
            name='variable',
            field=models.ForeignKey(default=1, to='pyscada.Variable', on_delete=models.CASCADE),
            preserve_default=False,
        ),
    ]
