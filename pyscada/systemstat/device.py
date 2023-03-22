# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from pyscada.models import VariableProperty, Variable
from pyscada.device import GenericDevice, GenericHandlerDevice
from . import PROTOCOL_ID

import os
import socket
from ftplib import FTP, error_perm, error_temp, error_reply, error_proto
from ipaddress import ip_address
from socket import gethostbyaddr, gaierror, herror
import datetime

from django.conf import settings

from asgiref.sync import async_to_sync, sync_to_async
from asyncio import wait_for
try:
    from asyncio.exceptions import TimeoutError as asyncioTimeoutError
    from asyncio.exceptions import CancelledError as asyncioCancelledError
except ModuleNotFoundError:
    # for python version < 3.8
    from asyncio import TimeoutError as asyncioTimeoutError
    from asyncio import CancelledError as asyncioCancelledError

from time import time, sleep
import logging

logger = logging.getLogger(__name__)

driver_ok = True
try:
    import psutil
except ImportError:
    logger.error("Cannot import psutil")
    driver_ok = False
try:
    import paramiko
except ImportError:
    logger.error("Cannot import paramiko")
    driver_ok = False

MEDIA_ROOT = settings.MEDIA_ROOT \
    if hasattr(settings, 'MEDIA_ROOT') else '/var/www/pyscada/http/media/'
MEDIA_URL = settings.MEDIA_URL \
    if hasattr(settings, 'MEDIA_URL') else '/media/'


class Device(GenericDevice):
    def __init__(self, device):
        self.driver_ok = driver_ok
        self.handler_class = Handler
        super().__init__(device)

        for var in self.device.variable_set.filter(active=1):
            if not hasattr(var, 'systemstatvariable'):
                continue
            self.variables[var.pk] = var


class Handler(GenericHandlerDevice):

    def __init__(self, pyscada_device, variables):
        super().__init__(pyscada_device, variables)
        self._protocol = PROTOCOL_ID
        self.driver_ok = driver_ok
        self.shell = None

    def connect(self):
        super().connect()
        try:
            self.inst = paramiko.SSHClient()
            self.inst.load_system_host_keys()
            self.inst.set_missing_host_key_policy(paramiko.WarningPolicy())
            self.inst.connect(self._device.systemstatdevice.host,
                              self._device.systemstatdevice.port,
                              self._device.systemstatdevice.username,
                              self._device.systemstatdevice.password,
                              timeout=self._device.systemstatdevice.timeout)
            channel = self.inst.get_transport().open_session()
            channel.get_pty()
            self.shell = self.inst.invoke_shell()
            sleep(1)
            while self.shell.recv_ready():
                self.shell.recv(1)
            return True
        except (socket.gaierror, paramiko.ssh_exception.SSHException, OSError,
                socket.timeout, paramiko.ssh_exception.AuthenticationException,
                paramiko.ssh_exception.NoValidConnectionsError) as e:
            self._not_accessible_reason = e
            self.inst = None
            return False

    def disconnect(self):
        if self.inst is not None:
            self.inst.close()
            self.inst = None
            return True
        return False

    def write_data(self, variable_id, value, task):
        var = Variable.objects.get(id=variable_id)
        cmd = var.systemstatvariable.parameter
        if var.systemstatvariable.information == 21:
            if var.device.systemstatdevice.system_type == 0:
                os.popen('nohup sh ' + str(cmd) + ' &\n')
            elif var.device.systemstatdevice.system_type == 1:
                if self.connect():
                    self.accessibility()
                    try:
                        result = ''
                        self.shell.send('nohup sh ' + str(cmd) + ' &\n')
                        sleep(self._device.systemstatdevice.timeout)
                        while self.shell.recv_ready():
                            try:
                                result += self.shell.recv(1).decode()
                            except UnicodeDecodeError:
                                pass
                        if result != '':
                            logger.debug(f'Writing to variable {var} return {result}')
                        error = ''
                        while self.shell.recv_stderr_ready():
                            try:
                                error += self.shell.recv_stderr(1).decode()
                            except UnicodeDecodeError:
                                pass
                        if error != '':
                            logger.warning(f'Writing to variable {var} return error {error}')
                    except (socket.gaierror, paramiko.ssh_exception.SSHException, OSError,
                            socket.timeout, paramiko.ssh_exception.AuthenticationException,
                            paramiko.ssh_exception.NoValidConnectionsError) as e:
                        self._not_accessible_reason = e
                        self.inst = None
                        self.accessibility()
                self.disconnect()
            return not value  # release the button
        else:
            logger.warning("Systemstat cannot write %s to variable id %s" % (value, variable_id))
            return None  # return None to set the device write task as failed

    def read_data_all(self, variables_dict):
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
        (20,'process_pid'),
        (40,'file or directory last modification time'),
        ### APCUPSD Status
        (100, 'STATUS'), # True/False
        (101, 'LINEV'), # Volts
        (102, 'BATTV'), # Volts
        (103, 'BCHARGE'), # %
        (104, 'TIMELEFT'), # Minutes
        (105, 'LOADPCT'), #
        ### List files in directory
        (200, 'list files'), #
        (201, 'list ftp files'), #
        ### Systemd services
        (250, 'is enabled'), #
        (251, 'is active'), #
        ### Datetime as timestamp
        (300, 'is active'), #
        """

        if not driver_ok:
            return None

        output = []
        apcupsd_status_is_queried = False
        for item in variables_dict.values():
            #item = variables_dict[item]
            timestamp = time()
            value = None
            if item.systemstatvariable.information == 0:
                # cpu_percent
                if hasattr(psutil, 'cpu_percent'):
                    cmd = 'psutil.cpu_percent()'
                    ssh_prefix = 'import psutil;'
                    value = self.exec_python_cmd(cmd, ssh_prefix=ssh_prefix)
                    timestamp = time()
            elif item.systemstatvariable.information == 1:
                # virtual_memory_total
                if hasattr(psutil, 'virtual_memory'):
                    cmd = 'psutil.virtual_memory().total'
                    ssh_prefix = 'import psutil;'
                    value = self.exec_python_cmd(cmd, ssh_prefix=ssh_prefix)
                    timestamp = time()
            elif item.systemstatvariable.information == 2:
                # virtual_memory_available
                if hasattr(psutil, 'virtual_memory'):
                    cmd = 'psutil.virtual_memory().available'
                    ssh_prefix = 'import psutil;'
                    value = self.exec_python_cmd(cmd, ssh_prefix=ssh_prefix)
                    timestamp = time()
            elif item.systemstatvariable.information == 3:
                # virtual_memory_percent
                if hasattr(psutil, 'virtual_memory'):
                    cmd = 'psutil.virtual_memory().percent'
                    ssh_prefix = 'import psutil;'
                    value = self.exec_python_cmd(cmd, ssh_prefix=ssh_prefix)
                    timestamp = time()
            elif item.systemstatvariable.information == 4:
                # virtual_memory_used
                if hasattr(psutil, 'virtual_memory'):
                    cmd = 'psutil.virtual_memory().used'
                    ssh_prefix = 'import psutil;'
                    value = self.exec_python_cmd(cmd, ssh_prefix=ssh_prefix)
                    timestamp = time()
            elif item.systemstatvariable.information == 5:
                # virtual_memory_free
                if hasattr(psutil, 'virtual_memory'):
                    cmd = 'psutil.virtual_memory().free'
                    ssh_prefix = 'import psutil;'
                    value = self.exec_python_cmd(cmd, ssh_prefix=ssh_prefix)
                    timestamp = time()
            elif item.systemstatvariable.information == 6:
                # virtual_memory_active
                if hasattr(psutil, 'virtual_memory'):
                    cmd = 'psutil.virtual_memory().active'
                    ssh_prefix = 'import psutil;'
                    value = self.exec_python_cmd(cmd, ssh_prefix=ssh_prefix)
                    timestamp = time()
            elif item.systemstatvariable.information == 7:
                # virtual_memory_inactive
                if hasattr(psutil, 'virtual_memory'):
                    cmd = 'psutil.virtual_memory().inactive'
                    ssh_prefix = 'import psutil;'
                    value = self.exec_python_cmd(cmd, ssh_prefix=ssh_prefix)
                    timestamp = time()
            elif item.systemstatvariable.information == 8:
                # virtual_memory_buffers
                if hasattr(psutil, 'virtual_memory'):
                    cmd = 'psutil.virtual_memory().buffers'
                    ssh_prefix = 'import psutil;'
                    value = self.exec_python_cmd(cmd, ssh_prefix=ssh_prefix)
                    timestamp = time()
            elif item.systemstatvariable.information == 9:
                # virtual_memory_cached
                if hasattr(psutil, 'virtual_memory'):
                    cmd = 'psutil.virtual_memory().cached'
                    ssh_prefix = 'import psutil;'
                    value = self.exec_python_cmd(cmd, ssh_prefix=ssh_prefix)
                    timestamp = time()
            elif item.systemstatvariable.information == 10:
                # swap_memory_total
                if hasattr(psutil, 'swap_memory'):
                    cmd = 'psutil.swap_memory().total'
                    ssh_prefix = 'import psutil;'
                    value = self.exec_python_cmd(cmd, ssh_prefix=ssh_prefix)
                    timestamp = time()
            elif item.systemstatvariable.information == 11:
                # swap_memory_used
                if hasattr(psutil, 'swap_memory'):
                    cmd = 'psutil.swap_memory().used'
                    ssh_prefix = 'import psutil;'
                    value = self.exec_python_cmd(cmd, ssh_prefix=ssh_prefix)
                    timestamp = time()
            elif item.systemstatvariable.information == 12:
                # swap_memory_free
                if hasattr(psutil, 'swap_memory'):
                    cmd = 'psutil.swap_memory().free'
                    ssh_prefix = 'import psutil;'
                    value = self.exec_python_cmd(cmd, ssh_prefix=ssh_prefix)
                    timestamp = time()
            elif item.systemstatvariable.information == 13:
                # swap_memory_percent
                if hasattr(psutil, 'swap_memory'):
                    cmd = 'psutil.swap_memory().percent'
                    ssh_prefix = 'import psutil;'
                    value = self.exec_python_cmd(cmd, ssh_prefix=ssh_prefix)
                    timestamp = time()
            elif item.systemstatvariable.information == 14:
                # swap_memory_sin
                if hasattr(psutil, 'swap_memory'):
                    cmd = 'psutil.swap_memory().sin'
                    ssh_prefix = 'import psutil;'
                    value = self.exec_python_cmd(cmd, ssh_prefix=ssh_prefix)
                    timestamp = time()
            elif item.systemstatvariable.information == 15:
                # swap_memory_sout
                if hasattr(psutil, 'swap_memory'):
                    cmd = 'psutil.swap_memory().sout'
                    ssh_prefix = 'import psutil;'
                    value = self.exec_python_cmd(cmd, ssh_prefix=ssh_prefix)
                    timestamp = time()
            elif item.systemstatvariable.information == 17:
                # disk_usage_systemdisk_percent
                if hasattr(psutil, 'disk_usage'):
                    cmd = 'psutil.disk_usage("/").percent'
                    ssh_prefix = 'import psutil;'
                    value = self.exec_python_cmd(cmd, ssh_prefix=ssh_prefix)
                    timestamp = time()
            elif item.systemstatvariable.information == 18:
                # disk_usage_disk_percent
                if hasattr(psutil, 'disk_usage'):
                    try:
                        cmd = 'async_to_sync(self._wait_for)(psutil.disk_usage, 10, "' + str(item.systemstatvariable.parameter) + '").percent'
                        ssh_cmd = 'psutil.disk_usage("' + str(item.systemstatvariable.parameter) + '").percent'
                        ssh_prefix = 'import psutil;'
                        value = self.exec_python_cmd(cmd, ssh_cmd, ssh_prefix)
                    except OSError:
                        value = None
                    except asyncioTimeoutError:
                        value = None
                    timestamp = time()
            elif item.systemstatvariable.information == 19:
                # ip_addresses
                if hasattr(psutil, 'net_if_addrs'):
                    param = item.systemstatvariable.parameter
                    try:
                        cmd = 'psutil.net_if_addrs()["' + str(param) + '"][0][1]'
                        ssh_prefix = 'import psutil;'
                        value = self.exec_python_cmd(cmd, ssh_prefix=ssh_prefix)
                    except KeyError as e:
                        value = f"Interface {param} not found"
                    except Exception as e:
                        value = e
                    timestamp = time()
            elif item.systemstatvariable.information == 20:
                processName = item.systemstatvariable.parameter
                # Check if process name contains the given name string. Return the pid.
                if self._device.systemstatdevice.system_type == 0:
                    value = -3
                    for proc in psutil.process_iter():
                        try:
                            for cmd in proc.cmdline():
                                if processName.lower() in cmd.lower():
                                    value = proc.pid
                                    break
                        except psutil.ZombieProcess:
                            value = -1
                        except psutil.AccessDenied:
                            value = -2
                        except psutil.NoSuchProcess:
                            value = -3
                elif self._device.systemstatdevice.system_type == 1:
                    cmd = "value"
                    ssh_prefix = f'import psutil\nvalue=-3\nfor proc in psutil.process_iter():\n    try:\n        for cmd in proc.cmdline():\n            if "{processName}".lower() in cmd.lower() and "for proc in psutil.process_iter():" not in cmd.lower():\n                value = proc.pid\n                break\n    except psutil.ZombieProcess:\n        value = -1\n    except psutil.AccessDenied:\n        value = -2\n    except psutil.NoSuchProcess:\n        value = -3\n'
                    value = self.exec_python_cmd(cmd, ssh_prefix=ssh_prefix)
                    value = -3 if value == '' else value
            elif item.systemstatvariable.information == 40:
                try:
                    cmd = 'os.path.getmtime("' + str(item.systemstatvariable.parameter) + '")'
                    ssh_prefix = 'import os;'
                    value = self.exec_python_cmd(cmd, ssh_prefix=ssh_prefix)
                except FileNotFoundError:
                    logger.warning(f"File or directory {param} not found. Cannot get last modification time.")
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
                        list_dir = async_to_sync(self._wait_for)(os.listdir, 10, vp.name)
                        list_dir = list(filter(os.path.isfile, list_dir))
                        list_dir.sort(key=os.path.getmtime)
                    except asyncioTimeoutError:
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
                                        if MEDIA_ROOT in vp.name:
                                            result += '<a href="' + MEDIA_URL + vp.name.replace(MEDIA_ROOT, "") +\
                                                      str(i) + '" target="_blank">' + str(i) + "</a><br>"
                                        else:
                                            result += str(i) + "<br>"
                                elif param[0] == "last":
                                    for i in list_dir[-val:]:
                                        if MEDIA_ROOT in vp.name:
                                            result += '<a href="' + MEDIA_URL + vp.name.replace(MEDIA_ROOT, "") +\
                                                      str(i) + '" target="_blank">' + str(i) + "</a><br>"
                                        else:
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
                        except (herror, gaierror, ValueError):
                            err = "FTP listing directory : first argument must be IP or known FQDN (/etc/hosts), " \
                                  "it's : " + param[0]
                            logger.debug(err)
                            VariableProperty.objects.update_property(variable_property=vp, value=err)
                            continue
                    try:
                        ftp = FTP(param[0])
                        ftp.login()
                        list_dir = async_to_sync(self._wait_for)(ftp.nlst, 10, vp.name)
                        ftp.close()
                    except asyncioTimeoutError:
                        VariableProperty.objects.update_property(variable_property=vp,
                                                                 value=str("Timeout : " + vp.name))
                        continue
                    except error_perm:
                        VariableProperty.objects.update_property(variable_property=vp,
                                                                 value=str(vp.name + " not found"))
                        continue
                    except error_temp:
                        VariableProperty.objects.update_property(variable_property=vp,
                                                                 value=str("Connection error"))
                        continue
                    except error_reply:
                        VariableProperty.objects.update_property(variable_property=vp,
                                                                 value=str("Reply error"))
                        continue
                    except error_proto:
                        VariableProperty.objects.update_property(variable_property=vp,
                                                                 value=str("Protocol error"))
                        continue
                    except OSError:
                        VariableProperty.objects.update_property(variable_property=vp,
                                                                 value=str("Device offline ?"))
                        continue
                    if list_dir is None or len(list_dir) == 0:
                        VariableProperty.objects.update_property(variable_property=vp,
                                                                 value=str("No files in ftp://" + param[0] +
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
            elif item.systemstatvariable.information == 250:
                # Result of systemctl is-enabled PROCESS_NAME
                cmd = "systemctl is-enabled " + str(item.systemstatvariable.parameter)
                value = self.exec_cmd(cmd)
                value = 13 if value == '' else value
                if type(value) == str:
                    value = value.replace('\n', '')
            elif item.systemstatvariable.information == 251:
                # Result of systemctl is-active PROCESS_NAME
                cmd = "systemctl is-active " + str(item.systemstatvariable.parameter)
                value = self.exec_cmd(cmd)
                value = 7 if value == '' else value
                if type(value) == str:
                    value = value.replace('\n', '')
            else:
                value = None
            # update variable
            if value is not None and item.update_value(value, timestamp):
                output.append(item.create_recorded_data_element())

        return output

    async def _wait_for(self, cmd, timeout=1, *args):
        return await wait_for(sync_to_async(cmd)(*args), timeout=timeout)

    def exec_python_cmd(self, cmd, ssh_cmd=None, ssh_prefix=""):

        value = None
        if self._device.systemstatdevice.system_type == 0:
            value = eval(cmd)
        elif self._device.systemstatdevice.system_type == 1:
            hostname = self._device.systemstatdevice.host
            port = self._device.systemstatdevice.port
            username = self._device.systemstatdevice.username
            password = self._device.systemstatdevice.password
            timeout = self._device.systemstatdevice.timeout
            if ssh_cmd is not None:
                cmd = ssh_cmd
            inst = paramiko.SSHClient()
            inst.load_system_host_keys()
            inst.set_missing_host_key_policy(paramiko.WarningPolicy())
            try:
                inst.connect(hostname, port, username, password, timeout=timeout)
                i, o, e = inst.exec_command("""python3 -c '""" + str(ssh_prefix) + """print(""" + str(cmd) + """)'""",
                                            timeout=timeout)
                err = e.read().decode()
                err = err[:-1] if err.endswith('\n')else err
                if err != '':
                    logger.error(f'Error {err} while running on {self._device} command {cmd}')
                value = o.read().decode()
                value = value[:-1] if value.endswith('\n') else value
                value = None if value == '' else value
                inst.close()
            except (socket.gaierror, paramiko.ssh_exception.SSHException, OSError,
                    socket.timeout, paramiko.ssh_exception.AuthenticationException,
                    paramiko.ssh_exception.NoValidConnectionsError) as e:
                pass
            if value == '' and err != '':
                logger.warning(f'Error running remote command {cmd} on {hostname}, returns : {err}')
                value = None
            value = None if value == 'None' else value
        return value

    def exec_cmd(self, cmd, ssh_cmd=None):
        value = None
        if self._device.systemstatdevice.system_type == 0:
            value = os.popen(cmd).read()
        elif self._device.systemstatdevice.system_type == 1:
            hostname = self._device.systemstatdevice.host
            port = self._device.systemstatdevice.port
            username = self._device.systemstatdevice.username
            password = self._device.systemstatdevice.password
            timeout = self._device.systemstatdevice.timeout
            if ssh_cmd is not None:
                cmd = ssh_cmd
            inst = paramiko.SSHClient()
            inst.load_system_host_keys()
            inst.set_missing_host_key_policy(paramiko.WarningPolicy())
            try:
                inst.connect(hostname, port, username, password, timeout=timeout)
                i, o, e = inst.exec_command(str(cmd), timeout=timeout)
                err = e.read().decode()
                value = o.read().decode()
                inst.close()
            except (socket.gaierror, paramiko.ssh_exception.SSHException, OSError,
                    socket.timeout, paramiko.ssh_exception.AuthenticationException,
                    paramiko.ssh_exception.NoValidConnectionsError) as e:
                pass
            if value == '' and err != '':
                logger.warning(f'Error running remote command {cmd} on {hostname}, returns : {err}')
                value = None
        return value


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
