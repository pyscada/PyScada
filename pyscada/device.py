# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.models import DeviceProtocol, VariableProperty
import pyscada

import sys
from time import time, sleep, time_ns
import logging

logger = logging.getLogger(__name__)

PROTOCOL_ID = None
driver_ok = True


class GenericHandlerDevice:
    """
    Generic handler device
    """

    def __init__(self, pyscada_device, variables):
        self._device = pyscada_device
        self._variables = variables
        self.inst = None
        self._device_not_accessible = 0
        self._not_accessible_reason = None
        if not hasattr(self, "_protocol"):
            self._protocol = PROTOCOL_ID
        if not hasattr(self, "driver_ok"):
            self.driver_ok = driver_ok

    def connect(self):
        """
        establish a connection to the Instrument
        """
        if not self.driver_ok:
            return False

        if self._device.protocol.id != self._protocol:
            try:
                p = DeviceProtocol.objects.get(id=self._protocol)
            except DeviceProtocol.DoesNotExist:
                p = None
            logger.warning(
                f"Wrong handler selected : it's for {p} device while device protocol is {self._device.protocol}"
            )
            return False

        # self.accessibility()

    def accessibility(self):
        if self.inst is not None:
            if self._device_not_accessible < 1:
                self._device_not_accessible = 1
                logger.info(f"Connected to device : {self._device}")
        else:
            if self._device_not_accessible > -1:
                self._device_not_accessible = -1
                msg = f"Device {self._device} is not accessible."
                if self._not_accessible_reason is not None:
                    msg += f" Reason : {self._not_accessible_reason}"
                    self._not_accessible_reason = None
                logger.info(msg)
        return True

    def disconnect(self):
        if self.inst is not None:
            self.inst = None
            return True
        return False

    def before_read(self):
        """
        will be called before the first read_data
        """
        return self.connect()

    def after_read(self):
        """
        will be called after the last read_data
        """
        return self.disconnect()

    def read_data(self, variable_instance):
        """
        read values from the device
        """
        logger.warning(
            f"Handler of {self._device} should overwrite read_data function."
        )
        return None

    def read_data_and_time(self, variable_instance):
        """
        read values and timestamps from the device
        """

        return self.read_data(variable_instance), self.time()

    def read_data_all(self, variables_dict):
        output = []

        if self.before_read():
            for item in variables_dict.values():
                value, read_time = self.read_data_and_time(item)

                if value is not None and item.update_value(value, read_time):
                    output.append(item.create_recorded_data_element())
        self.after_read()
        return output

    def write_data(self, variable_id, value, task):
        """
        write values to the device
        """
        if self.connect():
            for var in self._variables:
                var = self._variables[var]
                if variable_id == var.id:
                    logger.warning(
                        f"Handler of {self._device} should overwrite write_data function."
                    )
                    return None

            logger.warning(
                f"Variable {variable_id} not in variable list {self._variables} of device {self._device}"
            )
        return None

    def time(self):
        return time_ns() / 1000000000


class GenericDevice:
    """
    Generic device
    """

    def __init__(self, device):
        self.variables = {}
        self.device = device
        if not hasattr(self, "driver_ok"):
            self.driver_ok = driver_ok

        if not self.driver_ok:
            logger.warning(f"Driver import failed for {self.device}")

        try:
            if (
                hasattr(self.device, "instrument_handler")
                and self.device.instrument_handler is not None
            ):
                if self.device.instrument_handler.handler_path is not None:
                    sys.path.append(self.device.instrument_handler.handler_path)
                mod = __import__(
                    self.device.instrument_handler.handler_class, fromlist=["Handler"]
                )
                device_handler = getattr(mod, "Handler")
                self._h = device_handler(self.device, self.variables)
            elif hasattr(self, "handler_class"):
                self._h = self.handler_class(self.device, self.variables)
            else:
                self._h = GenericHandlerDevice(self.device, self.variables)
            self.driver_handler_ok = True
        except ImportError:
            self.driver_handler_ok = False
            logger.error(
                f"Handler import error : {self.device.short_name}", exc_info=True
            )

        # Wait 5 seconds to let changes appears in DB.
        sleep(5)

        for var in self.device.variable_set.filter(active=1):
            if not hasattr(var, str(self.device.protocol.protocol) + "variable"):
                continue
            self.variables[var.pk] = var

    def request_data(self):
        output = []

        if not self.driver_ok or not self.driver_handler_ok:
            return output

        output = self._h.read_data_all(self.variables)

        return output

    def write_data(self, variable_id, value, task):
        """
        write value to a Serial Device
        """

        output = []
        if not self.driver_ok or not self.driver_handler_ok:
            return output

        for item in self.variables:
            if self.variables[item].id == variable_id:
                if not self.variables[item].writeable:
                    logger.info(
                        f"Variable '{self.variables[item]}' is not writeable. Write task refused."
                    )
                    return False
                read_value = self._h.write_data(variable_id, value, task)
                if read_value is not None and self.variables[item].update_value(
                    read_value, time_ns() / 1000000000
                ):
                    output.append(self.variables[item].create_recorded_data_element())
        return output
