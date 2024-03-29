# Generated by Django 2.2.8 on 2020-12-01 13:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("pyscada", "0078_auto_20201123_1906"),
        ("hmi", "0041_auto_20201002_0934"),
    ]

    operations = [
        migrations.AddField(
            model_name="chart",
            name="x_axis_linlog",
            field=models.BooleanField(
                default=False, help_text="False->Lin / True->Log"
            ),
        ),
        migrations.AddField(
            model_name="chart",
            name="x_axis_var",
            field=models.ForeignKey(
                default=None,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="x_axis_var",
                to="pyscada.Variable",
            ),
        ),
    ]
