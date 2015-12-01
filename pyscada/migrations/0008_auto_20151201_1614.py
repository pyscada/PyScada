# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pyscada', '0007_auto_20151201_1613'),
    ]

    operations = [
        migrations.AlterField(
            model_name='unit',
            name='udunit',
            field=models.CharField(default=b'', max_length=500, verbose_name=b'udUnit'),
            preserve_default=True,
        ),
    ]
