# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def move_time_values(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    RecordedEvent = apps.get_model("pyscada", "RecordedEvent")
    for item in RecordedEvent.objects.all():
        item.time_begin_new = item.time_begin.timestamp
        item.time_end_new = item.time_end.timestamp
        item.save()

class Migration(migrations.Migration):

    dependencies = [
        ('pyscada', '0018_auto_20160228_1623'),
    ]

    operations = [
        migrations.RunPython(move_time_values),
    ]