# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('export', '0004_exporttask'),
    ]

    operations = [
        migrations.AddField(
            model_name='exporttask',
            name='busy',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='exporttask',
            name='filename_suffix',
            field=models.CharField(default=b'', max_length=400, blank=True),
        ),
        migrations.AlterField(
            model_name='exporttask',
            name='label',
            field=models.CharField(default=b'', max_length=400, blank=True),
        ),
        migrations.AlterField(
            model_name='exporttask',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
