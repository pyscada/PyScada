# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from pyscada.models import VariableProperty

try:
    import psutil
    driver_ok = True
except ImportError:
    driver_ok = False

import os
import concurrent.futures
from ftplib import FTP, error_perm
from ipaddress import ip_address
from socket import gethostbyaddr, gaierror, herror

from time import time
import logging

logger = logging.getLogger(__name__)

pool = concurrent.futures.ThreadPoolExecutor()


class Device:
    def __init__(self, device):
        self.variables = []
        self.device = device
        for var in device.variable_set.filter(active=1):
            if not hasattr(var, 'systemstatvariable'):
                continue
            self.variables.append(var)

    def request_data(self):
        """
        (0,'cpu_percent'),
        (1,'virtual_memory_total'),
        (2,'virtual_memory_available'),
        (3,'virtual_memory_percent'),
        (4,'virtual_memory_used'),
        (5,'virtual_memory_free'),
        (6,'virtual_memory_active'),
        (7,'virtual_memory_inactive'),
        (8,'virtual_memory_buffers'),
        (9,'virtual_memory_cached'),
        (10,'swap_memory_total'),
        (11,'swap_memory_used'),
        (12,'swap_memory_free'),
        (13,'swap_memory_percent'),
        (14,'swap_memory_sin'),
        (15,'swap_memory_sout'),
        (17,'disk_usage_systemdisk_percent'),
        (18,'disk_usage_disk_percent'),
        (19,'network_ip_address'),
        ### APCUPSD Status
        (100, 'STATUS'), # True/False
        (101, 'LINEV'), # Volts
        (102, 'BATTV'), # Volts
        (103, 'BCHARGE'), # %
        (104, 'TIMELEFT'), # Minutes
        (105, 'LOADPCT'), #
        ### Other
        (200, 'list_files'), #



        """
        if not driver_ok:
            return None

        output = []
        apcupsd_status_is_queried = False
        for item in self.variables:
            timestamp = time()
            value = None
            if item.systemstatvariable.information == 0:
                # cpu_percent
                if hasattr(psutil, 'cpu_percent'):
                    value = psutil.cpu_percent()
                    timestamp = time()
            elif item.systemstatvariable.information == 1:
                # virtual_memory_total
                if hasattr(psutil, 'virtual_memory'):
                    value = psutil.virtual_memory().total
                    timestamp = time()
            elif item.systemstatvariable.information == 2:
                # virtual_memory_available
                if hasattr(psutil, 'virtual_memory'):
                    value = psutil.virtual_memory().available
                    timestamp = time()
            elif item.systemstatvariable.information == 3:
                # virtual_memory_percent
                if hasattr(psutil, 'virtual_memory'):
                    value = psutil.virtual_memory().percent
                    timestamp = time()
            elif item.systemstatvariable.information == 4:
                # virtual_memory_used
                if hasattr(psutil, 'virtual_memory'):
                    value = psutil.virtual_memory().used
                    timestamp = time()
            elif item.systemstatvariable.information == 5:
                # virtual_memory_free
                if hasattr(psutil, 'virtual_memory'):
                    value = psutil.virtual_memory().free
                    timestamp = time()
            elif item.systemstatvariable.information == 6:
                # virtual_memory_active
                if hasattr(psutil, 'virtual_memory'):
                    value = psutil.virtual_memory().active
                    timestamp = time()
            elif item.systemstatvariable.information == 7:
                # virtual_memory_inactive
                if hasattr(psutil, 'virtual_memory'):
                    value = psutil.virtual_memory().inactive
                    timestamp = time()
            elif item.systemstatvariable.information == 8:
                # virtual_memory_buffers
                if hasattr(psutil, 'virtual_memory'):
                    value = psutil.virtual_memory().buffers
                    timestamp = time()
            elif item.systemstatvariable.information == 9:
                # virtual_memory_cached
                if hasattr(psutil, 'virtual_memory'):
                    value = psutil.virtual_memory().cached
                    timestamp = time()
            elif item.systemstatvariable.information == 10:
                # swap_memory_total
                if hasattr(psutil, 'swap_memory'):
                    value = psutil.swap_memory().total
                    timestamp = time()
            elif item.systemstatvariable.information == 11:
                # swap_memory_used
                if hasattr(psutil, 'swap_memory'):
                    value = psutil.swap_memory().used
                    timestamp = time()
            elif item.systemstatvariable.information == 12:
                # swap_memory_free
                if hasattr(psutil, 'swap_memory'):
                    value = psutil.swap_memory().free
                    timestamp = time()
            elif item.systemstatvariable.information == 13:
                # swap_memory_percent
                if hasattr(psutil, 'swap_memory'):
                    value = psutil.swap_memory().percent
                    timestamp = time()
            elif item.systemstatvariable.information == 14:
                # swap_memory_sin
                if hasattr(psutil, 'swap_memory'):
                    value = psutil.swap_memory().sin
                    timestamp = time()
            elif item.systemstatvariable.information == 15:
                # swap_memory_sout
                if hasattr(psutil, 'swap_memory'):
                    value = psutil.swap_memory().sout
                    timestamp = time()
            elif item.systemstatvariable.information == 17:
                # disk_usage_systemdisk_percent
                if hasattr(psutil, 'disk_usage'):
                    value = psutil.disk_usage('/').percent
                    timestamp = time()
            elif item.systemstatvariable.information == 18:
                # disk_usage_disk_percent
                if hasattr(psutil, 'disk_usage'):
                    try:
                        value = psutil.disk_usage(item.systemstatvariable.parameter).percent
                    except OSError:
                        value = None
                    timestamp = time()
            elif item.systemstatvariable.information == 19:
                # ip_addresses
                if hasattr(psutil, 'net_if_addrs'):
                    for vp in VariableProperty.objects.filter(variable=item):
                        try:
                            VariableProperty.objects.update_property(variable_property=vp,
                                                                     value=psutil.net_if_addrs()[vp.name][0][1])
                        except KeyError:
                            VariableProperty.objects.update_property(variable_property=vp,
                                                                     value="None")
                    value = None
                    timestamp = time()
            elif 100 <= item.systemstatvariable.information <= 105:
                # APCUPSD Status
                apcupsd_status = None
                if not apcupsd_status_is_queried:
                    apcupsd_status = query_apsupsd_status()
                    apcupsd_status_is_queried = True
                if apcupsd_status is not None:
                    if item.systemstatvariable.information == 100:
                        if 'STATUS' in apcupsd_status:
                            value = apcupsd_status['STATUS']
                            timestamp = apcupsd_status['timestamp']
                    elif item.systemstatvariable.information == 101:
                        if 'LINEV' in apcupsd_status:
                            value = apcupsd_status['LINEV']
                            timestamp = apcupsd_status['timestamp']
                    elif item.systemstatvariable.information == 102:
                        if 'BATTV' in apcupsd_status:
                            value = apcupsd_status['BATTV']
                            timestamp = apcupsd_status['timestamp']
                    elif item.systemstatvariable.information == 103:
                        if 'BCHARGE' in apcupsd_status:
                            value = apcupsd_status['BCHARGE']
                            timestamp = apcupsd_status['timestamp']
                    elif item.systemstatvariable.information == 104:
                        if 'TIMELEFT' in apcupsd_status:
                            value = apcupsd_status['TIMELEFT']
                            timestamp = apcupsd_status['timestamp']
                    elif item.systemstatvariable.information == 105:
                        if 'LOADPCT' in apcupsd_status:
                            value = apcupsd_status['LOADPCT']
                            timestamp = apcupsd_status['timestamp']
            elif item.systemstatvariable.information == 200:
                # list first X/last X/all items of a directory
                param = item.systemstatvariable.parameter
                if param is None:
                    param = ""
                if param != "":
                    param = param.split()
                for vp in VariableProperty.objects.filter(variable=item):
                    result = ""
                    try:
                        os.chdir(vp.name)
                        future = pool.submit(os.listdir, vp.name)
                        timeout = 10
                        list_dir = future.result(timeout)
                        list_dir = list(filter(os.path.isfile, list_dir))
                        list_dir.sort(key=os.path.getmtime)
                    except concurrent.futures.TimeoutError:
                        VariableProperty.objects.update_property(variable_property=vp,
                                                                 value=str("Timeout : " + vp.name))
                        continue
                    except FileNotFoundError:
                        VariableProperty.objects.update_property(variable_property=vp,
                                                                 value=str(vp.name + " not found"))
                        continue
                    except OSError as e:
                        VariableProperty.objects.update_property(variable_property=vp,
                                                                 value=str(vp.name + " - OSError"))
                        continue
                    if list_dir is None or len(list_dir) == 0:
                        VariableProperty.objects.update_property(variable_property=vp,
                                                                 value=str("No files in " + vp.name))
                        continue
                    if len(param) == 2:
                        try:
                            val = int(param[1])
                            if val <= 1:
                                VariableProperty.objects.update_property(variable_property=vp,
                                                                         value="Systemstat listing directory filter "
                                                                               "value must be > 0")
                                continue
                            else:
                                if param[0] == "first":
                                    for i in list_dir[:val]:
                                        result += str(i) + "<br>"
                                elif param[0] == "last":
                                    for i in list_dir[-val:]:
                                        result += str(i) + "<br>"
                                else:
                                    VariableProperty.objects.update_property(variable_property=vp,
                                                                             value="Systemstat listing directory "
                                                                                   "syntax error")
                                    continue
                        except ValueError:
                            VariableProperty.objects.update_property(variable_property=vp,
                                                                     value="Systemstat listing directory filter value "
                                                                           "must be an integer")
                            continue
                    elif (len(param) == 1 and param[0] == "all") or len(param) == 0:
                        for i in list_dir:
                            result += str(i) + "\r\n"
                    else:
                        VariableProperty.objects.update_property(variable_property=vp,
                                                                 value="Systemstat listing directory parameter error")
                        continue
                    VariableProperty.objects.update_property(variable_property=vp, value=result)
                value = None
                timestamp = time()
            elif item.systemstatvariable.information == 201:
                # list first X/last X/all items of a ftp directory
                param = item.systemstatvariable.parameter
                if param is None:
                    param = ""
                if param != "":
                    param = param.split()
                for vp in VariableProperty.objects.filter(variable=item):
                    result = ""
                    if len(param) == 0:
                        logger.debug("FTP IP missing for listing directory")
                        continue
                    try:
                        ip_address(param[0])
                    except ValueError:
                        try:
                            param[0] = gethostbyaddr(param[0])[2][0]
                            ip_address(param[0])
                        except herror or gaierror or ValueError:
                            err = "FTP listing directory : first argument must be IP or known FQDN (/etc/hosts), " \
                                  "it's : " + param[0]
                            logger.debug(err)
                            VariableProperty.objects.update_property(variable_property=vp, value=err)
                            continue
                    try:
                        ftp = FTP(param[0])
                        ftp.login()
                        future = pool.submit(ftp.nlst, vp.name)
                        timeout = 10
                        list_dir = future.result(timeout)
                        ftp.close()
                    except concurrent.futures.TimeoutError:
                        VariableProperty.objects.update_property(variable_property=vp,
                                                                 value=str("Timeout : " + vp.name))
                        continue
                    except error_perm:
                        VariableProperty.objects.update_property(variable_property=vp,
                                                                 value=str(vp.name + " not found"))
                        continue
                    except OSError:
                        VariableProperty.objects.update_property(variable_property=vp,
                                                                 value=str("Device offline ?"))
                        continue
                    if list_dir is None or len(list_dir) == 0:
                        VariableProperty.objects.update_property(variable_property=vp,
                                                                 value=str("No files in ftp://" + param[0] + "/" +
                                                                           vp.name))
                        continue
                    if len(param) == 3:
                        try:
                            val = int(param[2])
                            if val <= 1:
                                VariableProperty.objects.update_property(variable_property=vp,
                                                                         value="Systemstat listing directory filter "
                                                                               "value must be > 0")
                                continue
                            else:
                                if param[1] == "first":
                                    for i in list_dir[:val]:
                                        result += str(i) + "<br>"
                                elif param[1] == "last":
                                    for i in list_dir[-val:]:
                                        result += str(i) + "<br>"
                                else:
                                    VariableProperty.objects.update_property(variable_property=vp,
                                                                             value="Systemstat listing directory "
                                                                                   "syntax error")
                                    continue
                        except ValueError:
                            VariableProperty.objects.update_property(variable_property=vp,
                                                                     value="Systemstat listing directory filter value "
                                                                           "must be an integer")
                            continue
                    elif (len(param) == 2 and param[1] == "all") or len(param) == 1:
                        for i in list_dir:
                            result += str(i) + "\r\n"
                    else:
                        VariableProperty.objects.update_property(variable_property=vp,
                                                                 value="Systemstat listing directory parameter error")
                        continue
                    VariableProperty.objects.update_property(variable_property=vp, value=result)
                value = None
                timestamp = time()
            else:
                value = None
            # update variable
            if value is not None and item.update_value(value, timestamp):
                output.append(item.create_recorded_data_element())

        return output


def query_apsupsd_status():
    """
    (100, 'STATUS'), # True/False
    (101, 'LINEV'), # Volts
    (102, 'BATTV'), # Volts
    (103, 'BCHARGE'), # %
    (104, 'TIMELEFT'), # Minutes
    (105, 'LOADPCT'), # %

    """
    import subprocess
    output = {}
    try:
        apc_status = subprocess.check_output("/sbin/apcaccess")
    except:
        return None
    output['timestamp'] = time()
    for line in apc_status.split('\n'):
        (key, spl, val) = line.partition(': ')
        key = key.rstrip().upper()
        val = val.strip()
        val = val.split(' ')[0]
        if key == 'STATUS':
            output[key] = True if val.upper() == 'ONLINE' else False
        elif key in ['LINEV', 'BATTV', 'BCHARGE', 'TIMELEFT', 'LOADPCT']:
            output[key] = float(val)

    return output
