# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-07-04 13:07
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("pyscada", "0043_devicewritetask_property_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="devicewritetask",
            name="variable_property",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="pyscada.VariableProperty",
            ),
        ),
        migrations.AddField(
            model_name="variableproperty",
            name="value_class",
            field=models.CharField(
                choices=[
                    ("FLOAT32", "REAL (FLOAT32)"),
                    ("FLOAT32", "SINGLE (FLOAT32)"),
                    ("FLOAT32", "FLOAT32"),
                    ("UNIXTIMEF32", "UNIXTIMEF32"),
                    ("FLOAT64", "LREAL (FLOAT64)"),
                    ("FLOAT64", "FLOAT  (FLOAT64)"),
                    ("FLOAT64", "DOUBLE (FLOAT64)"),
                    ("FLOAT64", "FLOAT64"),
                    ("UNIXTIMEF64", "UNIXTIMEF64"),
                    ("INT64", "INT64"),
                    ("UINT64", "UINT64"),
                    ("UNIXTIMEI64", "UNIXTIMEI64"),
                    ("UNIXTIMEI32", "UNIXTIMEI32"),
                    ("INT32", "INT32"),
                    ("UINT32", "DWORD (UINT32)"),
                    ("UINT32", "UINT32"),
                    ("INT16", "INT (INT16)"),
                    ("INT16", "INT16"),
                    ("UINT16", "WORD (UINT16)"),
                    ("UINT16", "UINT (UINT16)"),
                    ("UINT16", "UINT16"),
                    ("BOOLEAN", "BOOL (BOOLEAN)"),
                    ("BOOLEAN", "BOOLEAN"),
                ],
                default="FLOAT64",
                max_length=15,
                verbose_name="value_class",
            ),
        ),
        migrations.AlterField(
            model_name="devicewritetask",
            name="variable",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="pyscada.Variable",
            ),
        ),
    ]
