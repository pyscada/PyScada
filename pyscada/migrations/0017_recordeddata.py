# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pyscada', '0016_auto_20160215_2002'),
    ]

    operations = [
        migrations.CreateModel(
            name='RecordedData',
            fields=[
                ('id', models.BigIntegerField(serialize=False, primary_key=True)),
                ('value_boolean', models.BooleanField(default=False)),
                ('value_int16', models.SmallIntegerField(null=True, blank=True)),
                ('value_int32', models.IntegerField(null=True, blank=True)),
                ('value_int64', models.BigIntegerField(null=True, blank=True)),
                ('value_float64', models.FloatField(null=True, blank=True)),
                ('variable', models.ForeignKey(to='pyscada.Variable')),
            ],
        ),
    ]
