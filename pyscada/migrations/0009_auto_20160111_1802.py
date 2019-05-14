# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pyscada', '0008_auto_20151201_1614'),
    ]

    operations = [
        migrations.AlterField(
            model_name='backgroundtask',
            name='identifier',
            field=models.CharField(default=b'', max_length=400, blank=True),
        ),
        migrations.AlterField(
            model_name='variable',
            name='name',
            field=models.SlugField(unique=True, max_length=80, verbose_name='variable name'),
        ),
    ]
