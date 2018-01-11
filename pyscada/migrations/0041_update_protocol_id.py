# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.systemstat import PROTOCOL_ID as systemstat_PROTOCOL_ID
from pyscada.modbus import PROTOCOL_ID as modbus_PROTOCOL_ID
from pyscada.visa import PROTOCOL_ID as visa_PROTOCOL_ID
from pyscada.onewire import PROTOCOL_ID as onewire_PROTOCOL_ID
from pyscada.phant import PROTOCOL_ID as phant_PROTOCOL_ID
from pyscada.smbus import PROTOCOL_ID as smbus_PROTOCOL_ID

from django.db import migrations


def forwards_func(apps, schema_editor):
    # We get the model from the versioned app registry;
    # if we directly import it, it'll be the wrong version
    DeviceProtocol = apps.get_model("pyscada", "DeviceProtocol")
    Device = apps.get_model("pyscada", "Device")
    db_alias = schema_editor.connection.alias
    protocol_list = []
    protocol_ids = {'systemstat':systemstat_PROTOCOL_ID,
                    'modbus': modbus_PROTOCOL_ID,
                    'visa': visa_PROTOCOL_ID,
                    'onewire': onewire_PROTOCOL_ID,
                    'phant': phant_PROTOCOL_ID,
                    'smbus': smbus_PROTOCOL_ID}

    # create intermediate device protocol schema
    for dp in DeviceProtocol.objects.using(db_alias).all():
        if dp.protocol in protocol_ids:
            DeviceProtocol.objects.using(db_alias).bulk_create(
                [DeviceProtocol( pk=dp.pk+100,
                                    protocol=dp.protocol,
                                    description=dp.description,
                                    app_name=dp.app_name,
                                    device_class=dp.device_class,
                                    daq_daemon=dp.daq_daemon,
                                    single_thread=dp.single_thread)])
            protocol_list.append([dp.pk+100,protocol_ids[dp.protocol]]) # save intermediate device protocol id
            Device.objects.using(db_alias).filter(protocol_id=dp.pk).update(protocol_id=dp.pk+100)
        else:
            if dp.pk < 10:
                # todo handle that right
                DeviceProtocol.objects.using(db_alias).bulk_create(
                    [DeviceProtocol(pk=dp.pk + 10,
                                    protocol=dp.protocol,
                                    description=dp.description,
                                    app_name=dp.app_name,
                                    device_class=dp.device_class,
                                    daq_daemon=dp.daq_daemon,
                                    single_thread=dp.single_thread)])
                Device.objects.using(db_alias).filter(protocol_id=dp.pk).update(protocol_id=dp.pk + 10)

    # delete all old device protocol schema
    DeviceProtocol.objects.using(db_alias).filter(pk__range=(2,100)).delete()
    # create new device protocol schema
    DeviceProtocol.objects.using(db_alias).bulk_create([
        DeviceProtocol(pk=systemstat_PROTOCOL_ID,
                       protocol='systemstat',
                       description='Local System Monitoring',
                       app_name='pyscada.systemstat',
                       device_class='pyscada.systemstat.device',
                       daq_daemon=True,
                       single_thread=True),
        DeviceProtocol(pk=modbus_PROTOCOL_ID,
                       protocol='modbus',
                       description='Modbus Device',
                       app_name='pyscada.modbus',
                       device_class='pyscada.modbus.device',
                       daq_daemon=True,
                       single_thread=True),
        DeviceProtocol(pk=visa_PROTOCOL_ID,
                       protocol='visa',
                       description='VISA Device',
                       app_name='pyscada.visa',
                       device_class='pyscada.visa.device',
                       daq_daemon=True,
                       single_thread=True),
        DeviceProtocol(pk=onewire_PROTOCOL_ID,
                       protocol='onewire',
                       description='1Wire Device',
                       app_name='pyscada.onewire',
                       device_class='pyscada.onewire.device',
                       daq_daemon=True,
                       single_thread=True),
        DeviceProtocol(pk=phant_PROTOCOL_ID,
                       protocol='phant',
                       description='Phant Webservice Device',
                       app_name='pyscada.phant',
                       device_class='None',
                       daq_daemon=False,
                       single_thread=True),
        DeviceProtocol(pk=smbus_PROTOCOL_ID,
                       protocol='smbus',
                       description='SMBus/I2C Device',
                       app_name='pyscada.smbus',
                       device_class='pyscada.smbus.device',
                       daq_daemon=True,
                       single_thread=True),
    ])
    # migrate intermediate protocol ids to new protocol ids
    for p_ids in protocol_list:
        Device.objects.using(db_alias).filter(protocol_id=p_ids[0]).update(protocol_id=p_ids[1])
    # delete intermediate protocol ids
    DeviceProtocol.objects.using(db_alias).filter(pk__gte=100).delete()

def reverse_func(apps, schema_editor):
    # forwards_func() creates two Country instances,
    # so reverse_func() should delete them.
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('pyscada', '0040_auto_20170905_0942'),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ]
