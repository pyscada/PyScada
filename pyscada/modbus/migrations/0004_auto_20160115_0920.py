# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pyscada', '0010_auto_20160115_0918'),
        ('modbus', '0003_auto_20160115_0918'),
    ]

    operations = [
        migrations.RenameField(
            model_name='modbusdevice',
            old_name='modbus_client',
            new_name='modbus_device',
        ),
    ]
