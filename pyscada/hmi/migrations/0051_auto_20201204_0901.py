# Generated by Django 2.2.17 on 2020-12-03 21:01

from django.db import migrations

from time import time
import logging

logger = logging.getLogger(__name__)

dd_dict = {}
control_element_dict = {}


def move_dropdown_in_control_panel(apps, schema_editor):
    control_item_model = apps.get_model("hmi.ControlItem")
    control_panel_model = apps.get_model("hmi.ControlPanel")
    control_panel_model_set = control_panel_model.objects.all()
    form_model = apps.get_model("hmi.Form")
    form_model_set = form_model.objects.all()
    count = 0
    timeout = time() + 60 * 5
    for item in control_panel_model_set:
        for dd in item.dropdowns.all():
            item.items.add(
                control_item_model.objects.get(id=control_element_dict[dd.id])
            )

            if time() > timeout:
                break

            count += 1

    for item in form_model_set:
        for dd in item.dropdowns.all():
            item.control_items.add(
                control_item_model.objects.get(id=control_element_dict[dd.id])
            )

            if time() > timeout:
                break

            count += 1

    logger.info("move %d dropdown in total\n" % count)


def move_dropdown(apps, schema_editor):
    dropdown = apps.get_model("hmi.DropDown")
    control_item_model = apps.get_model("hmi.ControlItem")
    control_element_option_model = apps.get_model("hmi.ControlElementOption")
    dropdown_set = dropdown.objects.all()
    count = 0
    timeout = time() + 60 * 5
    for item in dropdown_set:
        control_item = control_item_model(
            label=item.label,
            position=0,
            type=0,
            variable=item.variable,
            variable_property=item.variable_property,
            display_value_options=None,
            control_element_options=control_element_option_model.objects.get(
                id=dd_dict[item.id]
            ),
        )
        control_item.save()
        control_element_dict[item.id] = control_item.id

        if time() > timeout:
            break

        count += 1

    logger.info("move %d dropdown in total\n" % count)


def create_control_element_option(apps, schema_editor):
    dropdown = apps.get_model("hmi.DropDown")
    control_element_option_model = apps.get_model("hmi.ControlElementOption")
    dropdown_set = dropdown.objects.all()
    count = 0
    timeout = time() + 60 * 5
    for item in dropdown_set:
        control_element_option = control_element_option_model(
            name=item.label,
            placeholder=item.empty_value,
            dictionary=item.dictionary,
            empty_dictionary=item.empty,
        )
        control_element_option.save()
        dd_dict[item.id] = control_element_option.id

        if time() > timeout:
            break

        count += 1

    logger.info("create %d control element option in total\n" % count)


class Migration(migrations.Migration):
    dependencies = [
        ("hmi", "0050_auto_20201203_2101"),
    ]

    operations = [
        migrations.RunPython(
            create_control_element_option, reverse_code=migrations.RunPython.noop
        ),
        migrations.RunPython(move_dropdown, reverse_code=migrations.RunPython.noop),
        migrations.RunPython(
            move_dropdown_in_control_panel, reverse_code=migrations.RunPython.noop
        ),
    ]
