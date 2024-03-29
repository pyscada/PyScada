# Generated by Django 2.2.8 on 2021-11-25 12:56

from django.db import migrations, models
import logging

logger = logging.getLogger(__name__)

charts_dict = {}


def move_dicts(apps, schema_editor):
    HMIDictionaries = apps.get_model("hmi", "Dictionary")
    HMIDictionaryItems = apps.get_model("hmi", "DictionaryItem")
    Dictionaries = apps.get_model("pyscada", "Dictionary")
    DictionaryItems = apps.get_model("pyscada", "DictionaryItem")
    Variables = apps.get_model("pyscada", "Variable")
    ControlItems = apps.get_model("hmi", "ControlItem")
    db_alias = schema_editor.connection.alias

    hmi_dict_set = HMIDictionaries.objects.all()
    hmi_dictitems_set = HMIDictionaryItems.objects.all()
    var_set = Variables.objects.all()
    count = 0
    dict = []
    for item in hmi_dict_set:
        d = Dictionaries(
            id=item.id,
            name=item.name,
        )
        dict.append(d)
        count += 1
    logger.info("moved %d Dictionaries\n" % count)
    Dictionaries.objects.using(db_alias).bulk_create(dict)

    count = 0
    dictitems = []
    for item in hmi_dictitems_set:
        di = DictionaryItems(
            id=item.id,
            label=item.label,
            value=item.value,
            dictionary_id=item.dictionary.id,
        )
        dictitems.append(di)
        count += 1
    logger.info("moved %d DictionaryItems\n" % count)
    DictionaryItems.objects.using(db_alias).bulk_create(dictitems)

    count = 0
    variables = []
    for item in var_set:
        CId = ControlItems.objects.filter(
            variable=item,
            display_value_options__isnull=False,
            display_value_options__dictionary__isnull=False,
        )
        if len(CId):
            item.dictionary = Dictionaries.objects.get(
                id=CId.first().display_value_options.dictionary.id
            )
            variables.append(item)
            count += 1
        else:
            CIc = ControlItems.objects.filter(
                variable=item,
                control_element_options__isnull=False,
                control_element_options__dictionary__isnull=False,
            )
            if len(CIc):
                item.dictionary = Dictionaries.objects.get(
                    id=CIc.first().control_element_options.dictionary.id
                )
                variables.append(item)
                count += 1

    logger.info("moved %d dictionaries to variables\n" % count)
    Variables.objects.using(db_alias).bulk_update(variables, ["dictionary"])


class Migration(migrations.Migration):
    dependencies = [
        ("pyscada", "0093_auto_20211125_1256"),
        ("hmi", "0054_displayvalueoption_type"),
    ]

    operations = [
        migrations.RunPython(move_dicts, reverse_code=migrations.RunPython.noop),
    ]
