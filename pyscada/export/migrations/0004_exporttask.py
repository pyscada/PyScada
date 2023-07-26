# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):
    dependencies = [
        ("pyscada", "0023_auto_20160314_1817"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("export", "0003_auto_20160315_1140"),
    ]

    operations = [
        migrations.CreateModel(
            name="ExportTask",
            fields=[
                ("id", models.AutoField(serialize=False, primary_key=True)),
                ("label", models.CharField(default="", max_length=400)),
                (
                    "mean_value_period",
                    models.PositiveSmallIntegerField(
                        default=0, help_text="in Seconds (0 = no mean value)"
                    ),
                ),
                (
                    "file_format",
                    models.CharField(
                        default="hdf5",
                        max_length=400,
                        choices=[
                            ("hdf5", "Hierarchical Data Format Version 5"),
                            ("mat", "Matlab\xc2\xae mat v7.3 compatible file"),
                            (
                                "CSV_EXCEL",
                                "Microsoft\xc2\xae Excel\xc2\xae compatible csv file",
                            ),
                        ],
                    ),
                ),
                ("time_min", models.FloatField(default=None, null=True, blank=True)),
                ("time_max", models.FloatField(default=None, null=True, blank=True)),
                ("start", models.FloatField(default=0)),
                ("fineshed", models.FloatField(default=0, blank=True)),
                ("done", models.BooleanField(default=False)),
                ("failed", models.BooleanField(default=False)),
                (
                    "backgroundtask",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="pyscada.BackgroundTask",
                        null=True,
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                        null=True,
                    ),
                ),
                ("variables", models.ManyToManyField(to="pyscada.Variable")),
            ],
        ),
    ]
