# Generated by Django 3.2 on 2022-06-20 08:54

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("hmi", "0064_auto_20220617_1333"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="groupdisplaypermission",
            name="charts",
        ),
        migrations.RemoveField(
            model_name="groupdisplaypermission",
            name="control_items",
        ),
        migrations.RemoveField(
            model_name="groupdisplaypermission",
            name="custom_html_panels",
        ),
        migrations.RemoveField(
            model_name="groupdisplaypermission",
            name="forms",
        ),
        migrations.RemoveField(
            model_name="groupdisplaypermission",
            name="pages",
        ),
        migrations.RemoveField(
            model_name="groupdisplaypermission",
            name="process_flow_diagram",
        ),
        migrations.RemoveField(
            model_name="groupdisplaypermission",
            name="sliding_panel_menus",
        ),
        migrations.RemoveField(
            model_name="groupdisplaypermission",
            name="views",
        ),
        migrations.RemoveField(
            model_name="groupdisplaypermission",
            name="widgets",
        ),
    ]
