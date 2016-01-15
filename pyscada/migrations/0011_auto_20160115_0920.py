# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pyscada', '0010_auto_20160115_0918'),
    ]

    operations = [
        migrations.RenameField(
            model_name='device',
            old_name='client_type',
            new_name='device_type',
        )
    ]
