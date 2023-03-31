# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pyscada', '0009_auto_20160111_1802'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Client',
            new_name='Device',
        ),
        migrations.RenameModel(
            old_name='ClientWriteTask',
            new_name='DeviceWriteTask',
        ),
        migrations.RenameField(
            model_name='variable',
            old_name='client',
            new_name='device',
        )
    ]
