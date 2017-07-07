#!/usr/bin/python
# -*- coding: utf-8 -*-
from pyscada import log
from pyscada.models import Device
from pyscada.models import Variable
from pyscada.models import Unit
from pyscada.models import DeviceWriteTask
from pyscada.models import BackgroundTask
from pyscada.models import RecordedData
from pyscada.modbus.models import ModbusVariable
from pyscada.modbus.models import ModbusDevice
from pyscada.models import Color
from pyscada.hmi.models import Chart

from django.contrib.auth.models import User
from django.conf import settings

import os
import json
import time, datetime
import traceback
from struct import *
import re


def extract_numbers_from_str(value_str):
    match = re.match(r"(([^0-9,^-]+)?)(?P<number>-?[0-9]+[.]?[0-9]+)", value_str, re.I)
    if match:
        match = match.groupdict()
        return float(match['number'])
    else:
        return None


def decode_bcd(values):
    """
    decode bcd as int to dec
    """

    bin_str_out = ''
    if isinstance(values, (int, long)):
        bin_str_out = bin(values)[2:].zfill(16)
        bin_str_out = bin_str_out[::-1]
    else:
        for value in values:
            binStr = bin(value)[2:].zfill(16)
            binStr = binStr[::-1]
            bin_str_out = binStr + bin_str_out

    dec_num = 0
    for i in range(len(bin_str_out) / 4):
        bcdNum = int(bin_str_out[(i * 4):(i + 1) * 4][::-1], 2)
        if bcdNum > 9:
            dec_num = -dec_num
        else:
            dec_num = dec_num + (bcdNum * pow(10, i))
    return dec_num


def export_xml_config_file(filename=None):
    """
    export of the Variable Configuration as XML file
    """
    from xml.dom.minidom import getDOMImplementation
    import sys
    # reload(sys)
    sys.setdefaultencoding('utf8')
    Meta = {}
    if hasattr(settings, 'PYSCADA_META'):
        if 'description' in settings.PYSCADA_META:
            Meta['description'] = settings.PYSCADA_META['description']
        else:
            Meta['description'] = 'None'
        if 'name' in settings.PYSCADA_META:
            Meta['name'] = settings.PYSCADA_META['name']
        else:
            Meta['name'] = 'None'
    else:
        Meta['description'] = 'None'
        Meta['name'] = 'None'

    Meta['version'] = '1.1'

    def field_(name, type_, value=None):
        f = xml_doc.createElement('field')
        f.setAttribute('name', name)
        f.setAttribute('type', type_)

        if type_.upper() in ['STRING', 'CHAR']:
            if value == '':
                value = ' '
            f.appendChild(xml_doc.createTextNode(value.encode('utf-8')))
        elif type_.upper() in ['BOOLEAN']:
            if value:
                f.appendChild(xml_doc.createTextNode('True'))
            else:
                f.appendChild(xml_doc.createTextNode('False'))
        elif type_.upper() in ['UINT8', 'UINT16', 'UINT32', 'INT8', 'INT16', 'INT32', 'FLOAT64', 'FLOAT32']:
            f.appendChild(xml_doc.createTextNode(value.__str__()))
        else:
            f.appendChild(xml_doc.createTextNode(' '))
        return f

    impl = getDOMImplementation()
    xml_doc = impl.createDocument(None, "objects", None)
    doc_node = xml_doc.documentElement
    doc_node.setAttribute('version', Meta['version'])
    obj = xml_doc.createElement('object')
    obj.setAttribute('name', 'Meta')
    # creation_date (string)
    obj.appendChild(field_('creation_date', 'string', time.strftime('%d-%b-%Y %H:%M:%S')))
    # name (string)
    obj.appendChild(field_('name', 'string', Meta['name']))
    # description (string)
    obj.appendChild(field_('description', 'string', Meta['description']))
    doc_node.appendChild(obj)

    # Variable (object)
    for item in Variable.objects.all():
        obj = xml_doc.createElement('object')
        obj.setAttribute('name', 'Variable')
        obj.setAttribute('id', item.pk.__str__())
        # name (string)
        obj.appendChild(field_('name', 'string', item.name))
        # description (string)
        obj.appendChild(field_('description', 'string', item.description))
        # active (boolean)
        obj.appendChild(field_('active', 'boolean', item.active))
        # writeable (boolean)
        obj.appendChild(field_('writeable', 'boolean', item.writeable))
        # value_class (string)
        obj.appendChild(field_('value_class', 'string', validate_value_class(item.value_class)))
        # device_id ()
        obj.appendChild(field_('device_id', 'uint16', item.device_id))
        # unit_id
        obj.appendChild(field_('unit_id', 'uint16', item.unit_id))
        if hasattr(item, 'modbusvariable'):
            # modbus.address
            obj.appendChild(field_('modbus.address', 'uint16', item.modbusvariable.address))
            # modbus.function_code_read
            obj.appendChild(field_('modbus.function_code_read', 'uint8', item.modbusvariable.function_code_read))
        # hmi.chart_line_color_id
        obj.appendChild(field_('hmi.chart_line_color_id', 'uint16', item.chart_line_color_id))
        # hmi.short_name
        obj.appendChild(field_('hmi.short_name', 'string', item.short_name))
        # hmi.chart_line_thickness
        obj.appendChild(field_('hmi.chart_line_thickness', 'uint8', item.chart_line_thickness))

        # hdf.dims
        obj.appendChild(field_('hdf.dims', 'uint16', 1))
        doc_node.appendChild(obj)

    # Unit
    for item in Unit.objects.all():
        obj = xml_doc.createElement('object')
        obj.setAttribute('name', 'Unit')
        obj.setAttribute('id', item.pk.__str__())
        # unit (string)
        obj.appendChild(field_('unit', 'string', item.unit))
        # description (string)
        obj.appendChild(field_('description', 'string', item.description))
        # udunit (string)
        obj.appendChild(field_('udunit', 'string', item.udunit))
        doc_node.appendChild(obj)

    # Device
    for item in Device.objects.all():
        obj = xml_doc.createElement('object')
        obj.setAttribute('name', 'Device')
        obj.setAttribute('id', item.pk.__str__())
        # name (string)
        obj.appendChild(field_('name', 'string', item.short_name))
        # description (string)
        obj.appendChild(field_('description', 'string', item.description))
        # protocol (string)
        obj.appendChild(field_('protocol', 'string', item.protocol.protocol))
        # active (boolean)
        obj.appendChild(field_('active', 'boolean', item.active))
        if hasattr(item, 'modbusdevice'):
            # modbus.protocol (string)
            obj.appendChild(
                field_('modbus.protocol', 'string', item.modbusdevice.protocol_choices[item.modbusdevice.protocol][1]))
            # modbus.ip_address (string)
            obj.appendChild(field_('modbus.ip_address', 'string', item.modbusdevice.ip_address))
            # modbus.port (string)
            obj.appendChild(field_('modbus.port', 'string', item.modbusdevice.port))
            # modbus.unit_id (uint8)
            obj.appendChild(field_('modbus.unit_id', 'uint8', item.modbusdevice.unit_id))
        doc_node.appendChild(obj)

    # Color
    for item in Color.objects.all():
        obj = xml_doc.createElement('object')
        obj.setAttribute('name', 'Color')
        obj.setAttribute('id', item.pk.__str__())
        # name (string)
        obj.appendChild(field_('name', 'string', item.name))
        # R (uint8)
        obj.appendChild(field_('R', 'uint8', item.R))
        # G (uint8)
        obj.appendChild(field_('G', 'uint8', item.G))
        # B (uint8)
        obj.appendChild(field_('B', 'uint8', item.B))
        doc_node.appendChild(obj)

    # Chart
    for item in Chart.objects.all():
        obj = xml_doc.createElement('object')
        obj.setAttribute('name', 'Chart')
        obj.setAttribute('id', item.pk.__str__())
        # name (string)
        obj.appendChild(field_('title', 'string', item.title))
        # x_axis_label (string)
        obj.appendChild(field_('x_axis_label', 'string', item.x_axis_label))
        # x_axis_ticks (uint8)
        obj.appendChild(field_('x_axis_ticks', 'uint8', item.x_axis_ticks))
        # y_axis_label (string)
        obj.appendChild(field_('y_axis_label', 'string', item.y_axis_label))
        # y_axis_min (float64)
        obj.appendChild(field_('y_axis_min', 'float64', item.y_axis_min))
        # y_axis_max (float64)
        obj.appendChild(field_('y_axis_max', 'float64', item.y_axis_max))
        # variables (string)
        variables_list = item.variables_list();
        obj.appendChild(field_('variables', 'string', str(variables_list)))
        doc_node.appendChild(obj)

    if filename:
        with open(filename, "wb") as file_:
            xml_doc.writexml(file_, encoding='utf-8')
    else:
        return xml_doc.toprettyxml(encoding='utf-8')


def validate_value_class(class_str):
    if class_str.upper() in ['FLOAT64', 'DOUBLE', 'FLOAT', 'LREAL', 'UNIXTIMEF64']:
        return 'FLOAT64'
    if class_str.upper() in ['FLOAT32', 'SINGLE', 'REAL', 'UNIXTIMEF32']:
        return 'FLOAT32'
    if class_str.upper() in ['UINT64']:
        return 'UINT64'
    if class_str.upper() in ['INT64', 'UNIXTIMEI64']:
        return 'INT64'
    if class_str.upper() in ['INT32']:
        return 'INT32'
    if class_str.upper() in ['UINT32', 'DWORD', 'UNIXTIMEI32']:
        return 'UINT32'
    if class_str.upper() in ['INT16', 'INT']:
        return 'INT16'
    if class_str.upper() in ['UINT', 'UINT16', 'WORD']:
        return 'UINT16'
    if class_str.upper() in ['INT8']:
        return 'INT8'
    if class_str.upper() in ['UINT8', 'BYTE']:
        return 'UINT8'
    if class_str.upper() in ['BOOL', 'BOOLEAN']:
        return 'BOOLEAN'
    else:
        return 'FLOAT64'


def _cast(value, class_str):
    if class_str.upper() in ['FLOAT64', 'DOUBLE', 'FLOAT', 'LREAL', 'FLOAT32', 'SINGLE', 'REAL', 'UNIXTIMEF32',
                             'UNIXTIMEF64']:
        return float(value)
    if class_str.upper() in ['INT32', 'UINT32', 'DWORD', 'INT16', 'INT', 'UINT', 'UINT16', 'WORD', 'INT8', 'UINT8',
                             'BYTE']:
        return int(value)
    if class_str.upper() in ['BOOL', 'BOOLEAN']:
        return value.lower() == 'true'
    else:
        return value


## daemon
def daemon_run(label, handlerClass):
    pid = str(os.getpid())

    # init daemon

    try:
        mh = handlerClass()
        dt_set = mh.dt_set
    except:
        var = traceback.format_exc()
        log.error("exception while initialisation of %s:%s %s" % (label, os.linesep, var))
        raise
    # register the task in Backgroudtask list
    bt = BackgroundTask(start=time.time(), label=label, message='daemonized', timestamp=time.time(), pid=pid)
    bt.save()
    bt_id = bt.pk

    # mark the task as running
    bt = BackgroundTask.objects.get(pk=bt_id)
    bt.timestamp = time.time()
    bt.message = 'running...'
    bt.save()

    log.notice("started %s" % label)
    err_count = 0
    # main loop
    while not bt.stop_daemon:
        t_start = time.time()
        if bt.message == 'reinit':
            mh = handlerClass()
            bt = BackgroundTask.objects.get(pk=bt_id)
            bt.timestamp = time.time()
            bt.message = 'running...'
            bt.save()
            log.notice("reinit of %s daemon done" % label)
        try:
            # do actions
            data = mh.run()  # query data and write to database
            if data:
                RecordedData.objects.bulk_create(data)
            err_count = 0
        except:
            var = traceback.format_exc()
            err_count += 1
            # write log only
            if err_count <= 3 or err_count == 10 or err_count % 100 == 0:
                log.debug("occ: %d, exception in %s daemon%s%s %s" % (err_count, label, os.linesep, os.linesep, var), -1)

            # do actions
            mh = handlerClass()

        # update BackgroudtaskTask
        bt = BackgroundTask.objects.get(pk=bt_id)
        bt.timestamp = time.time()
        if dt_set > 0:
            bt.load = max(min((time.time() - t_start) / dt_set, 1), 0)
        else:
            bt.load = 1
        bt.save()
        dt = dt_set - (time.time() - t_start)
        if dt > 0:
            time.sleep(dt)

    # will be called after stop signal
    try:
        bt = BackgroundTask.objects.get(pk=bt_id)
        bt.timestamp = time.time()
        bt.done = True
        bt.message = 'stopped'
        bt.pid = 0
        bt.save()
    except:
        var = traceback.format_exc()
        log.error("exception while shutdownn of %s:%s %s" % (label, os.linesep, var))
    log.notice("stopped %s execution" % label)


def daq_daemon_run(label):
    """
    acquire data from the different devices/protocols
    """

    pid = str(os.getpid())
    devices = {}
    dt_set = 5
    # init daemons
    for item in Device.objects.filter(protocol__daq_daemon=1, active=1):
        try:
            tmp_device = item.get_device_instance()
            if tmp_device is not None:
                devices[item.pk] = tmp_device
                dt_set = min(dt_set, tmp_device.device.polling_interval)
        except:
            var = traceback.format_exc()
            log.error("exception while initialisation of %s:%s %s" % (label, os.linesep, var))
    # register the task in Backgroudtask list
    bt = BackgroundTask(start=time.time(), label=label, message='daemonized', timestamp=time.time(), pid=pid)
    bt.save()
    bt_id = bt.pk

    # mark the task as running
    bt = BackgroundTask.objects.get(pk=bt_id)
    bt.timestamp = time.time()
    bt.message = 'running...'
    bt.save()

    log.notice("started %s" % label)
    err_count = 0
    reinit_count = 0
    # main loop

    while not bt.stop_daemon:
        try:
            t_start = time.time()
            # handle reinit
            if bt.restart_daemon:
                reinit_count += 1
            # wait aprox 5 min (300s) runs befor reinit to avoid frequent reinits
            if bt.restart_daemon and reinit_count > 300.0 / dt_set:
                for item in Device.objects.filter(protocol__daq_daemon=1, active=1):
                    try:
                        tmp_device = item.get_device_instance()
                        if tmp_device is not None:
                            devices[item.pk] = tmp_device
                            dt_set = min(dt_set, tmp_device.device.polling_interval)
                    except:
                        var = traceback.format_exc()
                        log.error("exception while initialisation of %s:%s %s" % (label, os.linesep, var))

                bt = BackgroundTask.objects.get(pk=bt_id)
                bt.timestamp = time.time()
                bt.message = 'running...'
                bt.restart_daemon = False
                bt.save()
                log.notice("reinit of %s daemon done" % label)
                reinit_count = 0
            # process write tasks
            for task in DeviceWriteTask.objects.filter(done=False, start__lte=time.time(), failed=False):
                if not task.variable.scaling is None:
                    task.value = task.variable.scaling.scale_output_value(task.value)
                if task.variable.device_id in devices:
                    if devices[task.variable.device_id].write_data(task.variable.id, task.value):  # do write task
                        task.done = True
                        task.fineshed = time.time()
                        task.save()
                        log.notice('changed variable %s (new value %1.6g %s)' % (
                            task.variable.name, task.value, task.variable.unit.description), task.user)
                    else:
                        task.failed = True
                        task.fineshed = time.time()
                        task.save()
                        log.error('change of variable %s failed' % (task.variable.name), task.user)
                else:
                    task.failed = True
                    task.fineshed = time.time()
                    task.save()
                    log.error('device id not valid %d ' % (task.variable.device_id), task.user)

            # start the read tasks
            data = [[]]

            for item in devices.values():
                # todo check for polling interval
                # do actions
                tmp_data = item.request_data()  # query data
                if isinstance(tmp_data, list):
                    if len(tmp_data) > 0:
                        if len(data[-1]) + len(tmp_data) < 998:
                            # add to the last write job
                            data[-1] += tmp_data
                        else:
                            # add to next write job
                            data.append(tmp_data)

            # write data to the database
            for item in data:
                RecordedData.objects.bulk_create(item)
            # update BackgroudTask
            bt = BackgroundTask.objects.get(pk=bt_id)
            bt.timestamp = time.time()
            if dt_set > 0:
                bt.load = max(min((time.time() - t_start) / dt_set, 1), 0)
            else:
                bt.load = 1
            bt.save()
            dt = dt_set - (time.time() - t_start)
            if dt > 0:
                time.sleep(dt)
            err_count = 0
        except:
            var = traceback.format_exc()
            err_count += 1
            # write log only
            if err_count <= 3 or err_count % 10 == 0:
                log.debug("occ: %d, exception in %s daemon%s%s %s" % (err_count, label, os.linesep, os.linesep, var), -1)
            if err_count > 100:
                break

    # will be called after stop signal
    try:
        bt = BackgroundTask.objects.get(pk=bt_id)
        bt.timestamp = time.time()
        bt.done = True
        bt.message = 'stopped'
        bt.pid = 0
        bt.save()
    except:
        var = traceback.format_exc()
        log.error("exception while shutdown of %s:%s %s" % (label, os.linesep, var))
    log.notice("stopped %s execution" % label)
