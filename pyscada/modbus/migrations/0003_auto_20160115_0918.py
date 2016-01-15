# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pyscada', '0010_auto_20160115_0918'),
        ('modbus', '0002_auto_20160111_1802'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ModbusClient',
            new_name='ModbusDevice',
        )
    ]
