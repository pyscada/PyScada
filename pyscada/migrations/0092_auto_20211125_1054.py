# Generated by Django 2.2.8 on 2021-11-25 10:54

from django.db import migrations, models
import pyscada.models


class Migration(migrations.Migration):
    dependencies = [
        ("pyscada", "0091_auto_20211118_1019"),
    ]

    operations = [
        migrations.AlterField(
            model_name="periodicfield",
            name="start_from",
            field=models.DateTimeField(
                default=pyscada.models.start_from_default,
                help_text="Calculate from this DateTime and then each period_factor*period",
            ),
        ),
    ]
