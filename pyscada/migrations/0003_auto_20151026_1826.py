# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pyscada', '0002_event_hysteresis'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mailrecipient',
            name='to_email',
            field=models.EmailField(max_length=254),
        ),
    ]
