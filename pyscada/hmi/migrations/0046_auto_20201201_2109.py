# Generated by Django 2.2.17 on 2020-12-01 21:00

from django.db import migrations

from time import time
import logging

logger = logging.getLogger(__name__)

charts_dict = {}


def move_chart_vars(apps, schema_editor):
    chart_model = apps.get_model("hmi.Chart")
    chart_axis_model = apps.get_model("hmi.ChartAxis")
    for chart in charts_dict:
        item = chart_model.objects.get(id=chart)
        axis = chart_axis_model.objects.get(id=charts_dict[chart])
        axis.variables.set(item.variables.all())


def move_chart_axis(apps, schema_editor):
    chart_model = apps.get_model("hmi.Chart")
    chart_axis_model = apps.get_model("hmi.ChartAxis")
    chart_set = chart_model.objects.all()
    count = 0
    timeout = time() + 60 * 5
    for item in chart_set:
        axis = chart_axis_model(
            label=item.y_axis_label,
            min=item.y_axis_min,
            max=item.y_axis_max,
            show_plot_points=item.show_plot_points,
            show_plot_lines=item.show_plot_lines,
            stack=False,
            chart=chart_model.objects.get(id=item.id),
        )
        axis.save()
        charts_dict[item.id] = axis.id

        if time() > timeout:
            break

        count += 1

    logger.info("wrote %d lines in total\n" % count)


class Migration(migrations.Migration):
    dependencies = [
        ("hmi", "0045_auto_20201201_2100"),
    ]

    operations = [
        migrations.RunPython(move_chart_axis, reverse_code=migrations.RunPython.noop),
        migrations.RunPython(move_chart_vars, reverse_code=migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="chart",
            name="show_plot_lines",
        ),
        migrations.RemoveField(
            model_name="chart",
            name="show_plot_points",
        ),
        migrations.RemoveField(
            model_name="chart",
            name="variables",
        ),
        migrations.RemoveField(
            model_name="chart",
            name="y_axis_label",
        ),
        migrations.RemoveField(
            model_name="chart",
            name="y_axis_max",
        ),
        migrations.RemoveField(
            model_name="chart",
            name="y_axis_min",
        ),
        migrations.RemoveField(
            model_name="chart",
            name="y_axis_uniquescale",
        ),
    ]
