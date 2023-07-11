# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pyscada", "0022_auto_20160228_2029"),
    ]

    operations = [
        migrations.AlterField(
            model_name="device",
            name="device_type",
            field=models.CharField(
                default="generic",
                max_length=400,
                choices=[
                    ("generic", "no Protocol"),
                    ("systemstat", "Local System Monitoring"),
                    ("modbus", "Modbus Device"),
                    ("smbus", "SMBus/I2C Device"),
                ],
            ),
        ),
    ]
