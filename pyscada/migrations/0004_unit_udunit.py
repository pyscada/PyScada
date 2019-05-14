# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pyscada', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='unit',
            name='udunit',
            field=models.CharField(max_length=500, verbose_name='udUnit',default=''),
            preserve_default=True,
        ),
    ]