# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pyscada', '0028_auto_20160630_0831'),
    ]

    operations = [
        migrations.AddField(
            model_name='scaling',
            name='limit_input',
            field=models.BooleanField(default=0),
            preserve_default=False,
        ),
    ]
