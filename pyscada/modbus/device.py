# -*- coding: utf-8 -*-
from pyscada import log
from pyscada.modbus.utils import encode_value
#from pyscada.modbus.utils import get_bits_by_class
from pyscada.modbus.utils import decode_value
try:
    from pymodbus.client.sync import ModbusTcpClient
    from pymodbus.client.sync import ModbusSerialClient
    from pymodbus.client.sync import ModbusUdpClient
    from pymodbus.constants import Defaults
    driver_ok = True
except ImportError:
    driver_ok = False
    
from math import isnan, isinf
from time import time

class InputRegisterBlock:
    def __init__(self):
        self.variable_address   = [] #
        self.variable_length    = [] # in bytes
        self.value_class     = [] #
        self.variable_id        = [] #

    def insert_item(self,variable_id,variable_address,value_class,variable_length):
        if not self.variable_address:
            self.variable_address.append(variable_address)
            self.variable_length.append(variable_length)
            self.value_class.append(value_class)
            self.variable_id.append(variable_id)
        elif max(self.variable_address) < variable_address:
            self.variable_address.append(variable_address)
            self.variable_length.append(variable_length)
            self.value_class.append(value_class)
            self.variable_id.append(variable_id)
        elif min(self.variable_address) > variable_address:
            self.variable_address.insert(0,variable_address)
            self.variable_length.insert(0,variable_length)
            self.value_class.insert(0,value_class)
            self.variable_id.insert(0,variable_id)
        else:
            i = self.find_gap(self.variable_address,variable_address)
            if (i is not None):
                self.variable_address.insert(i,variable_address)
                self.variable_length.insert(i,variable_length)
                self.value_class.insert(i,value_class)
                self.variable_id.insert(i,variable_id)


    def request_data(self,slave,unit=0x00):
        quantity = sum(self.variable_length) # number of bits to read
        first_address = min(self.variable_address)
        
        try:
            result = slave.read_input_registers(first_address,quantity/16,unit=unit)
        except:
            # something went wrong (ie. Server/Slave is not excessible)
            return None
        if not hasattr(result, 'registers'):
            return None

        return self.decode_data(result)
        
    
    def decode_data(self,result):
        out = {}
        #var_count = 0
        for idx in range(len(self.variable_length)):
            tmp = []
            for i in range(self.variable_length[idx]/16):
                tmp.append(result.registers.pop(0))
            out[self.variable_id[idx]] = decode_value(tmp,self.value_class[idx])
            if isnan(out[self.variable_id[idx]]) or isinf(out[self.variable_id[idx]]):
                    out[self.variable_id[idx]] = None
        return out
    
    def find_gap(self,L,value):
        for index in range(len(L)):
            if L[index] == value:
                return None
            if L[index] > value:
                return index

class HoldingRegisterBlock(InputRegisterBlock):
    def request_data(self,slave,unit=0x00):
        quantity = sum(self.variable_length) # number of bits to read
        first_address = min(self.variable_address)
        try:
            result = slave.read_holding_registers(first_address,quantity/16,unit=unit)
        except:
            # something went wrong (ie. Server/Slave is not excessible) 
            return None   
        if not hasattr(result, 'registers'):
            return None

        return self.decode_data(result)

class CoilBlock:
    def __init__(self):
        self.variable_id            = [] #
        self.variable_address       = [] #
    
    def insert_item(self,variable_id,variable_address):
        if not self.variable_address:
            self.variable_address.append(variable_address)
            self.variable_id.append(variable_id)
        elif max(self.variable_address) < variable_address:
            self.variable_address.append(variable_address)
            self.variable_id.append(variable_id)
        elif min(self.variable_address) > variable_address:
            self.variable_address.insert(0,variable_address)
            self.variable_id.insert(0,variable_id)
        else:
            i = self.find_gap(self.variable_address,variable_address)
            if (i is not None):
                self.variable_address.insert(i,variable_address)
                self.variable_id.insert(i,variable_id)
    
    
    def request_data(self,slave,unit=0x00):
        """
        request data from the modbus slave/server
        """
        quantity = len(self.variable_address) # number of bits to read
        first_address = min(self.variable_address)
        try:
            result = slave.read_coils(first_address,quantity,unit=unit)
        except:
            # something went wrong (ie. Server/Slave is not excessible) 
            return None
            
            
        if not hasattr(result, 'bits'):
            return None
            
        return self.decode_data(result)
        

    def decode_data(self,result):
        """
        map/decode input bits to output bit array
        """
        out = {}
        for idx in self.variable_id:
            out[idx] = result.bits.pop(0)
        return out
    
    def find_gap(self,L,value):
        """
        try to find a address gap in the list of modbus registers
        """
        for index in range(len(L)):
            if L[index] == value:
                return None
            if L[index] > value:
                return index

class DiscreteInputBlock(CoilBlock):
    def request_data(self,slave,unit=0x00):
        quantity = len(self.variable_address) # number of bits to read
        first_address = min(self.variable_address)
        
        try:
            result = slave.read_discrete_inputs(first_address,quantity,unit=unit)
        except:
            # something went wrong (ie. Server/Slave is not excessible) 
            return None
        
        if not hasattr(result, 'bits'):
            return None
            
        return self.decode_data(result)


class Device:
    """
    Modbus device (Master) class
    """
    def __init__(self,device):
        self._device_inst           = device
        self._address               = device.modbusdevice.ip_address
        self._unit_id               = device.modbusdevice.unit_id
        self._port                  = device.modbusdevice.port
        self._protocol              = device.modbusdevice.protocol
        self._stopbits              = device.modbusdevice.stopbits
        self._bytesize              = device.modbusdevice.bytesize
        self._parity                = device.modbusdevice.parity
        self._baudrate              = device.modbusdevice.baudrate
        self._timeout               = device.modbusdevice.timeout
        self._device_not_accessible = False
        # stopbits
        if self._stopbits == 0:
            self._stopbits = Defaults.Stopbits
        # bytesize
        if self._bytesize == 0:
            self._bytesize = Defaults.Bytesize
        # parity
        parity_list = {0:Defaults.Parity,1:'N',2:'E',3:'O'}
        self._parity = parity_list[self._parity]
        # baudrate
        if self._baudrate == 0:
            self._baudrate = Defaults.Baudrate
        # timeout
        if self._timeout == 0:
            self._timeout = Defaults.Timeout
        
        self.trans_input_registers  = []
        self.trans_coils            = []
        self.trans_holding_registers = []
        self.trans_discrete_inputs  = []
        self.variables  = {}
        self._variable_config   = self._prepare_variable_config(device)
        self._not_accessible_variable = []
        self.data = []

        
    def _prepare_variable_config(self,device):
        
        for var in device.variable_set.filter(active=1):
            if not hasattr(var,'modbusvariable'):
                continue
            FC = var.modbusvariable.function_code_read
            if FC == 0:
                continue
            #address      = var.modbusvariable.address
            #bits_to_read = get_bits_by_class(var.value_class)
                
            #self.variables[var.pk] = {'value_class':var.value_class,'writeable':var.writeable,'record':var.record,'name':var.name,'adr':address,'bits':bits_to_read,'fc':FC}
            # self.variables[var.pk] = RecordData(var.pk,var.name,var.value_class,\
            #     var.writeable,adr=address,bits=bits_to_read,fc=FC,accessible=True,\
            #     record_value=var.record,scaling = var.scaling)
            
            # add some attr to the var model 
            var.add_attr(accessible=True)
            # add the var to the list of 
            self.variables[var.pk] = var
            
            
            if FC == 1: # coils
                self.trans_coils.append([var.modbusvariable.address,var.pk,FC])
            elif FC == 2: # discrete inputs
                self.trans_discrete_inputs.append([var.modbusvariable.address,var.pk,FC])
            elif FC == 3: # holding registers
                self.trans_holding_registers.append([var.modbusvariable.address,var.value_class,var.get_bits_by_class(),var.pk,FC])
            elif FC == 4: # input registers
                self.trans_input_registers.append([var.modbusvariable.address,var.value_class,var.get_bits_by_class(),var.pk,FC])
            else:
                continue

        self.trans_discrete_inputs.sort()
        self.trans_holding_registers.sort()
        self.trans_coils.sort()
        self.trans_input_registers.sort()
        out = []
        
        # input registers
        old = -2
        regcount = 0
        for entry in self.trans_input_registers:
            if (entry[0] != old) or regcount >122:
                regcount = 0
                out.append(InputRegisterBlock()) # start new register block
            out[-1].insert_item(entry[3],entry[0],entry[1],entry[2]) # add item to block
            old = entry[0] + entry[2]/16
            regcount += entry[2]/16
        
        # holding registers
        old = -2
        regcount = 0
        for entry in self.trans_holding_registers:
            if (entry[0] != old) or regcount >122:
                regcount = 0
                out.append(HoldingRegisterBlock()) # start new register block
            out[-1].insert_item(entry[3],entry[0],entry[1],entry[2]) # add item to block
            old = entry[0] + entry[2]/16
            regcount += entry[2]/16
        
        # coils
        old = -2
        for entry in self.trans_coils:
            if (entry[0] != old+1):
                out.append(CoilBlock()) # start new coil block
            out[-1].insert_item(entry[1],entry[0])
            old = entry[0]
        #  discrete inputs
        old = -2
        for entry in self.trans_discrete_inputs:
            if (entry[0] != old+1):
                out.append(DiscreteInputBlock()) # start new coil block
            out[-1].insert_item(entry[1],entry[0])
            old = entry[0]
        return out


    def _connect(self):
        """
        connect to the modbus slave (server)
        """
        if self._protocol == 0: # TCP
            self.slave = ModbusTcpClient(self._address,int(self._port))
        elif self._protocol == 1: # UDP
            self.slave = ModbusUdpClient(self._address,int(self._port))
        elif self._protocol in (2,3,4): # serial
            method_list = {2:'ascii',3:'rtu',4:'binary'}
            self.slave = ModbusSerialClient( \
                method=method_list[self._protocol],\
                port=self._port,\
                stopbits=self._stopbits,\
                bytesize =self._bytesize,\
                parity   =self._parity,\
                baudrate =self._baudrate,\
                timeout  =self._timeout)
        else:
            raise NotImplementedError, "Protocol not supported"
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
            if not self._device_not_accessible:
                log.error("device with id: %d is not accessible"%(self._device_inst.pk))
            self._device_not_accessible = True
            return []
        output = []
        for register_block in self._variable_config:
            result = register_block.request_data(self.slave,self._unit_id)
            if result is None:
                self._disconnect()
                self._connect()
                result = register_block.request_data(self.slave,self._unit_id)
            
            if result is not None:
                for variable_id in register_block.variable_id:
                    if self.variables[variable_id].update_value(result[variable_id],time()):
                        output.append(self.variables[variable_id].create_recorded_data_element())
                    if not self.variables[variable_id].accessible:
                        log.info(("variable with id: %d is now accessible")%(variable_id))
                        self.variables[variable_id].accessible = True
                
            else:
                for variable_id in register_block.variable_id:
                    if self.variables[variable_id].accessible:
                        log.error(("variable with id: %d is not accessible")%(variable_id))
                        self.variables[variable_id].accessible = False
                        self.variables[variable_id].update_value(None,time())
        # reset device not accessible status 
        if self._device_not_accessible:
            log.info(("device with id: %d is now accessible")%(self._device_inst.pk))
            self._device_not_accessible = False
        
        self._disconnect()
        return output
    
    def write_data(self,variable_id, value):
        """
        write value to single modbus register or coil
        """
        if not self.variables[variable_id].writeable:
            return False

        if self.variables[variable_id].modbusvariable.function_code_read == 3:
            # write register
            if 0 <= self.variables[variable_id].modbusvariable.address <= 65535:
                
                self._connect()
                if self.variables[variable_id].get_bits_by_class()/16 == 1:
                    # just write the value to one register
                    self.slave.write_register(self.variables[variable_id].modbusvariable.address,int(value),unit=self._unit_id)
                else:
                    # encode it first
                    self.slave.write_registers(self.variables[variable_id].modbusvariable.address,list(encode_value(value,self.variables[variable_id].value_class)),unit=self._unit_id)
                self._disconnect()
                return True
            else:
                log.error('Modbus Address %d out of range'%self.variables[variable_id].modbusvariable.address)
                return False
        elif self.variables[variable_id].modbusvariable.function_code_read == 1:
            # write coil
            if 0 <= self.variables[variable_id].modbusvariable.address <= 65535:
                self._connect()
                self.slave.write_coil(self.variables[variable_id].modbusvariable.address,bool(value),unit=self._unit_id)
                self._disconnect()
                return True
            else:
                log.error('Modbus Address %d out of range'%self.variables[variable_id].modbusvariable.address)
        else:
            log.error('wrong function type %d'%self.variables[variable_id].modbusvariable.function_code_read)
            return False

