# -*- coding: utf-8 -*-
from __future__ import unicode_literals

try:
    from pymodbus.client.sync import ModbusTcpClient
    from pymodbus.client.sync import ModbusSerialClient
    from pymodbus.client.sync import ModbusUdpClient
    from pymodbus.constants import Defaults
    from pymodbus.transaction import ModbusBinaryFramer
    from pymodbus.transaction import ModbusAsciiFramer
    from pymodbus.transaction import ModbusRtuFramer
    from pymodbus.transaction import ModbusSocketFramer

    driver_ok = True
except ImportError:
    driver_ok = False

from math import isnan, isinf
from time import time
import logging

logger = logging.getLogger(__name__)


def find_gap(l, value):
    """
    try to find a address gap in the list of modbus registers
    """
    for index in range(len(l)):
        if l[index] == value:
            return None
        if l[index] > value:
            return index


def _default_decoder(value):
    return value[0]


class RegisterBlock:
    def __init__(self):
        self.registers_data = {}  # dict of modbus register addresses
        self.registers = []
        self.variables = {}
        self.register_size = 16  # in bits

    def insert_item(self, variable_id, variable_address, decode_value=_default_decoder, variable_length=1):
        self.variables[variable_id] = {
            'decode_function': decode_value,
            'len': variable_length,
            'registers': []
        }
        for idx in range(int(variable_length / self.register_size)):
            if not (variable_address + idx) in self.registers_data:
                # register will not be queried add register 
                self.registers_data[variable_address + idx] = None

            self.variables[variable_id]['registers'].append(variable_address + idx)
        self.registers = list(self.registers_data.keys())
        self.registers.sort()

    def check(self):
        """
        check the register block
        """
        # todo do check for gaps
        return True

    def _request_data(self, slave, unit, first_address, quantity):
        return slave.read_input_registers(first_address, quantity, unit=unit)

    def request_data(self, slave, unit=0x00):
        quantity = max(self.registers) - min(self.registers) + 1
        first_address = min(self.registers)

        try:
            result = self._request_data(slave, unit, first_address, quantity)
        except:
            # something went wrong (ie. Server/Slave is not accessible)
            # todo add log for some specific errors
            # var = traceback.format_exc()
            # log.error("exeption while request_data of %s" % (var))
            return None
        if hasattr(result, 'registers'):
            return self.decode_data(result.registers)
        elif hasattr(result, 'bits'):
            return self.decode_data(result.bits)
        else:
            return None

    def decode_data(self, result):
        out = {}
        # map result to the register
        for idx in self.registers:
            self.registers_data[idx] = result.pop(0)
        for v_id in self.variables:
            out[v_id] = self.variables[v_id]['decode_function'](
                [self.registers_data[k] for k in self.variables[v_id]['registers']])
            if type(out[v_id]) is float:
                if isnan(out[v_id]) or isinf(out[v_id]):
                    out[v_id] = None
        return out


class InputRegisterBlock(RegisterBlock):
    def _request_data(self, slave, unit, first_address, quantity):
        return slave.read_input_registers(first_address, quantity, unit=unit)


class HoldingRegisterBlock(RegisterBlock):
    def _request_data(self, slave, unit, first_address, quantity):
        return slave.read_holding_registers(first_address, quantity, unit=unit)


class CoilBlock(RegisterBlock):
    def __init__(self):
        RegisterBlock.__init__(self)
        self.register_size = 1  # in bitss

    def _request_data(self, slave, unit, first_address, quantity):
        return slave.read_coils(first_address, quantity, unit=unit)


class DiscreteInputBlock(RegisterBlock):
    def __init__(self):
        RegisterBlock.__init__(self)
        self.register_size = 1  # in bitss

    def _request_data(self, slave, unit, first_address, quantity):
        return slave.read_discrete_inputs(first_address, quantity, unit=unit)


class Device:
    """
    Modbus device (Master) class
    """

    def __init__(self, device):
        self.device = device
        self._address = device.modbusdevice.ip_address
        self._unit_id = device.modbusdevice.unit_id
        self._port = device.modbusdevice.port
        self._protocol = device.modbusdevice.protocol
        self._framer = device.modbusdevice.framer
        self._stopbits = device.modbusdevice.stopbits
        self._bytesize = device.modbusdevice.bytesize
        self._parity = device.modbusdevice.parity
        self._baudrate = device.modbusdevice.baudrate
        self._timeout = device.modbusdevice.timeout
        self._device_not_accessible = 0
        # stopbits
        if self._stopbits == 0:
            self._stopbits = Defaults.Stopbits
        # bytesize
        if self._bytesize == 0:
            self._bytesize = Defaults.Bytesize
        # parity
        parity_list = {0: Defaults.Parity, 1: 'N', 2: 'E', 3: 'O'}
        self._parity = parity_list[self._parity]
        # baudrate
        if self._baudrate == 0:
            self._baudrate = Defaults.Baudrate
        # timeout
        if self._timeout == 0:
            self._timeout = Defaults.Timeout

        self.trans_input_registers = []
        self.trans_coils = []
        self.trans_holding_registers = []
        self.trans_discrete_inputs = []
        self.variables = {}
        self._variable_config = self._prepare_variable_config(device)
        self.data = []

    def _prepare_variable_config(self, device):

        for var in device.variable_set.filter(active=1):
            if not hasattr(var, 'modbusvariable'):
                continue
            f_c = var.modbusvariable.function_code_read
            if f_c == 0:
                continue

            # add some attr to the var model 
            var.add_attr(accessible=1)
            # add the var to the list of 
            self.variables[var.pk] = var

            if f_c == 1:  # coils
                self.trans_coils.append([var.modbusvariable.address, var.pk, f_c])
            elif f_c == 2:  # discrete inputs
                self.trans_discrete_inputs.append([var.modbusvariable.address, var.pk, f_c])
            elif f_c == 3:  # holding registers
                self.trans_holding_registers.append(
                    [var.modbusvariable.address, var.decode_value, var.get_bits_by_class(), var.pk, f_c])
            elif f_c == 4:  # input registers
                self.trans_input_registers.append(
                    [var.modbusvariable.address, var.decode_value, var.get_bits_by_class(), var.pk, f_c])
            else:
                continue

        self.trans_discrete_inputs.sort(key=lambda x: x[0])
        self.trans_holding_registers.sort(key=lambda x: x[0])
        self.trans_coils.sort(key=lambda x: x[0])
        self.trans_input_registers.sort(key=lambda x: x[0])
        out = []

        # input registers
        old = -2
        regcount = 0
        for entry in self.trans_input_registers:
            if (entry[0] != old) or regcount > 122:
                regcount = 0
                out.append(InputRegisterBlock())  # start new register block
            out[-1].insert_item(entry[3], entry[0], entry[1], entry[2])  # add item to block
            old = entry[0] + entry[2] / 16
            regcount += entry[2] / 16

        # holding registers
        old = -2
        regcount = 0
        for entry in self.trans_holding_registers:
            if (entry[0] != old) or regcount > 122:
                regcount = 0
                out.append(HoldingRegisterBlock())  # start new register block
            out[-1].insert_item(entry[3], entry[0], entry[1], entry[2])  # add item to block
            old = entry[0] + entry[2] / 16
            regcount += entry[2] / 16

        # coils
        old = -2
        for entry in self.trans_coils:
            if entry[0] != old + 1:
                out.append(CoilBlock())  # start new coil block
            out[-1].insert_item(entry[1], entry[0])
            old = entry[0]
        # discrete inputs
        old = -2
        for entry in self.trans_discrete_inputs:
            if entry[0] != old + 1:
                out.append(DiscreteInputBlock())  # start new coil block
            out[-1].insert_item(entry[1], entry[0])
            old = entry[0]
        return out

    def _connect(self):
        """
        connect to the modbus slave (server)
        """
        framer = None
        if self._framer == 0:  # Socket Framer
            framer = ModbusSocketFramer
        elif self._framer == 1:  # RTU Framer
            framer = ModbusRtuFramer
        elif self._framer == 2:  # ASCII Framer
            framer = ModbusAsciiFramer
        elif self._framer == 3:  # Binary Framer
            framer = ModbusBinaryFramer
        if self._protocol == 0:  # TCP
            if self._framer is None:  # No Framer
                self.slave = ModbusTcpClient(self._address, int(self._port))
            else:
                self.slave = ModbusTcpClient(self._address, int(self._port), framer=framer)
        elif self._protocol == 1:  # UDP
            if self._framer is None:  # No Framer
                self.slave = ModbusUdpClient(self._address, int(self._port))
            else:
                self.slave = ModbusUdpClient(self._address, int(self._port), framer=framer)
        elif self._protocol in (2, 3, 4):  # serial
            method_list = {2: 'ascii', 3: 'rtu', 4: 'binary'}
            self.slave = ModbusSerialClient(
                method=method_list[self._protocol],
                port=self._port,
                stopbits=self._stopbits,
                bytesize=self._bytesize,
                parity=self._parity,
                baudrate=self._baudrate,
                timeout=self._timeout)
        else:
            raise NotImplementedError("Protocol not supported")
        status = self.slave.connect()
        return status

    def _disconnect(self):
        """
        close the connection to the modbus slave (server)
        """
        self.slave.close()

    def request_data(self):
        """
    
        """
        if not driver_ok:
            return None
        if not self._connect():
            if self._device_not_accessible == -1:  #
                logger.error("device with id: %d is not accessible" % self.device.pk)
            self._device_not_accessible -= 1
            return []
        output = []
        for register_block in self._variable_config:
            result = register_block.request_data(self.slave, self._unit_id)
            if result is None:
                self._disconnect()
                self._connect()
                result = register_block.request_data(self.slave, self._unit_id)

            if result is not None:
                for variable_id in register_block.variables:
                    if self.variables[variable_id].update_value(result[variable_id], time()):
                        recorded_data_element = self.variables[variable_id].create_recorded_data_element()
                        if recorded_data_element is not None:
                            output.append(recorded_data_element)
                    if self.variables[variable_id].accessible < 1:
                        logger.info("variable with id: %d is now accessible" % variable_id)
                        self.variables[variable_id].accessible = 1
            else:
                for variable_id in register_block.variables:
                    if self.variables[variable_id].accessible == -1:
                        logger.error("variable with id: %d is not accessible" % variable_id)
                        self.variables[variable_id].update_value(None, time())
                    self.variables[variable_id].accessible -= 1

        # reset device not accessible status 
        if self._device_not_accessible <= -1:
            logger.info("device with id: %d is now accessible" % self.device.pk)
        if self._device_not_accessible < 1:
            self._device_not_accessible = 1

        self._disconnect()
        return output

    def write_data(self, variable_id, value, task):
        """
        write value to single modbus register or coil
        """
        if variable_id not in self.variables:
            return False

        if not self.variables[variable_id].writeable:
            return False

        if self.variables[variable_id].modbusvariable.function_code_read == 3:
            # write register
            if 0 <= self.variables[variable_id].modbusvariable.address <= 65535:

                if self._connect():
                    if self.variables[variable_id].get_bits_by_class() / 16 == 1:
                        # just write the value to one register
                        self.slave.write_register(self.variables[variable_id].modbusvariable.address, int(value),
                                                  unit=self._unit_id)
                    else:
                        # encode it first
                        self.slave.write_registers(self.variables[variable_id].modbusvariable.address,
                                                   list(self.variables[variable_id].encode_value(value)),
                                                   unit=self._unit_id)
                    self._disconnect()
                    return True
                else:
                    logger.info("device with id: %d is now accessible" % self.device.pk)
                    return False
            else:
                logger.error('Modbus Address %d out of range' % self.variables[variable_id].modbusvariable.address)
                return False
        elif self.variables[variable_id].modbusvariable.function_code_read == 1:
            # write coil
            if 0 <= self.variables[variable_id].modbusvariable.address <= 65535:
                if self._connect():
                    self.slave.write_coil(self.variables[variable_id].modbusvariable.address, bool(value),
                                          unit=self._unit_id)
                    self._disconnect()
                    return True
                else:
                    logger.info("device with id: %d is now accessible" % self.device.pk)
                    return False
            else:
                logger.error('Modbus Address %d out of range' % self.variables[variable_id].modbusvariable.address)
        else:
            logger.error('wrong type of function code %d' %
                         self.variables[variable_id].modbusvariable.function_code_read)
            return False
