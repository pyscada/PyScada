# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-07-11 07:29
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("export", "0012_exporttask_backgroundprocess"),
    ]

    operations = [
        migrations.RenameField(
            model_name="exporttask",
            old_name="datetime_fineshed",
            new_name="datetime_finished",
        ),
    ]
