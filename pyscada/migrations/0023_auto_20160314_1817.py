# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pyscada', '0022_auto_20160228_2029'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='device_type',
            field=models.CharField(default=b'generic', max_length=400, choices=[(b'generic', b'no Protocol'), (b'systemstat', b'Local System Monitoring'), (b'modbus', b'Modbus Device'), (b'smbus', b'SMBus/I2C Device')]),
        ),
    ]
