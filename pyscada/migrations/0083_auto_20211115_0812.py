# Generated by Django 2.2.24 on 2021-11-15 08:12

import datetime
from django.db import migrations, models
from datetime import timezone


class Migration(migrations.Migration):
    dependencies = [
        ("pyscada", "0082_auto_20211112_1043"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="periodfield",
            name="offset_second",
        ),
        migrations.AddField(
            model_name="periodfield",
            name="start_from",
            field=models.DateTimeField(
                default=datetime.datetime(2021, 11, 15, 0, 0, tzinfo=timezone.utc),
                help_text="Count from this DateTime and then each period_factor*periodcalculate between 1min30 and 2min30 etc.",
            ),
        ),
    ]
