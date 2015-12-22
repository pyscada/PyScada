# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pyscada', '0006_auto_20151130_1449'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='MailQueue',
            new_name='Mail',
        ),
        migrations.AddField(
            model_name='backgroundtask',
            name='identifier',
            field=models.CharField(default=b'', max_length=400),
            preserve_default=True,
        ),
    ]
