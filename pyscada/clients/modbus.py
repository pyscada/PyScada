# -*- coding: utf-8 -*-
from pymodbus.client.sync import ModbusTcpClient
#from twisted.internet import reactor, protocol
from pyscada.utils import decode_value
from pyscada.utils import get_bits_by_class
from pyscada.utils.modbus import decode_address
from pyscada.utils import decode_bits
from pyscada.models import GlobalConfig
import random

class RegisterBlock:
    def __init__(self,client_address,client_port,sim=False):
        self.variable_address     = [] #
        self.variable_length     = [] # in bytes
        self.variable_class     = [] #
        self.variable_name         = [] #
        self.slave                = False # instance of the
        self._address             = client_address
        self._port                 = client_port
        self._sim               = sim


    def insert_item(self,variable_name,variable_address,variable_class,variable_length):
        if not self.variable_address:
            self.variable_address.append(variable_address)
            self.variable_length.append(variable_length)
            self.variable_class.append(variable_class)
            self.variable_name.append(variable_name)
        elif max(self.variable_address) < variable_address:
            self.variable_address.append(variable_address)
            self.variable_length.append(variable_length)
            self.variable_class.append(variable_class)
            self.variable_name.append(variable_name)
        elif min(self.variable_address) > variable_address:
            self.variable_address.insert(0,variable_address)
            self.variable_length.insert(0,variable_length)
            self.variable_class.insert(0,variable_class)
            self.variable_name.insert(0,variable_name)
        else:
            i = self.find_gap(self.variable_address,variable_address)
            if (i is not None):
                self.variable_address.insert(i,variable_address)
                self.variable_length.insert(i,variable_length)
                self.variable_class.insert(i,variable_class)
                self.variable_name.insert(i,variable_name)


    def request_data(self,slave):
        quantity = sum(self.variable_length) # number of bits to read
        first_address = self.variable_address[0]
        if not self._sim:
            result = slave.read_input_registers(first_address,quantity/16)
            if not hasattr(result, 'registers'):
                return result

        out = {}
        #var_count = 0
        for idx in range(len(self.variable_length)):
            tmp = []
            for i in range(self.variable_length[idx]/16):
                if self._sim:
                    tmp.append(int(random.randint(0,32000)))
                else:
                    tmp.append(result.registers.pop(0))
            out[self.variable_name[idx]] = decode_value(tmp,self.variable_class[idx])
        return out


    def find_gap(self,L,value):
        for index in range(len(L)):
            if L[index] == value:
                return None
            if L[index] > value:
                return index

class CoilBlock:
    def __init__(self,client_address,client_port,sim=False):
        self.variable_address       = {} #
        self.variable_name          = {} #
        self.slave                  = False # instance of the
        self._address               = client_address
        self._port                  = client_port
        self._sim                   = sim


    def insert_item(self,variable_name,variable_address):
            if not variable_address[0] in self.variable_address:
                self.variable_address[variable_address[0]] = []
                self.variable_name[variable_address[0]] = []
            self.variable_address[variable_address[0]].append(variable_address[1])
            self.variable_name[variable_address[0]].append(variable_name)



    def request_data(self,slave):
        quantity = len(self.variable_address) # number of bits to read
        first_address = self.variable_address.keys()[0]
        if not self._sim:
            result = slave.read_input_registers(first_address,quantity)
            if not hasattr(result, 'registers'):
                return result

        out = {}
        for register in self.variable_address:
            if not self._sim:
                tmp = decode_bits(result.registers.pop(0))
            else:
                tmp = decode_bits(int(random.randint(0,65535)))
            for idx,bit in enumerate(self.variable_address[register]):
                out[self.variable_name[register][idx]] = tmp[bit]

        return out


    def find_gap(self,L,value):
        for index in range(len(L)):
            if L[index] == value:
                return None
            if L[index] > value:
                return index
class client:
    """
    Modbus client (Master) class
    """
    def __init__(self,client_config):
        self._address           = client_config['modbus_ip']['ip']
        self._port              = client_config['modbus_ip']['port']
        self._silentMode        = GlobalConfig.objects.get_value_by_key('silentMode')
        self._sim               = bool(int(GlobalConfig.objects.get_value_by_key('simulation')))
        self._variable_config   = self._prepare_variable_config(client_config['variable_input_config'])
        

    def _prepare_variable_config(self,variable_config):
        trans_variable_config = []
        trans_variable_bit_config = []
        for idx in variable_config:
            Address = decode_address(variable_config[idx]['modbus_ip']['address'])
            bits_to_read =     get_bits_by_class(variable_config[idx]['class']);
            if isinstance(Address, list):
                trans_variable_bit_config.append([Address,idx])
            else:
                trans_variable_config.append([Address,variable_config[idx]['class'],bits_to_read,idx])

        trans_variable_config.sort()
        trans_variable_bit_config.sort()
        out = []
        old = -2
        regcount = 0
        #
        for entry in trans_variable_config:
            if (entry[0] != old) or regcount >122:
                regcount = 0
                out.append(RegisterBlock(self._address,self._port,self._sim)) # start new register block
            out[-1].insert_item(entry[3],entry[0],entry[1],entry[2]) # add item to block
            old = entry[0] + entry[2]/16
            regcount += entry[2]/16

        # bit registers
        old = -2
        for entry in trans_variable_bit_config:
            if (entry[0][0] != old and entry[0][0] != old+1):
                out.append(CoilBlock(self._address,self._port,self._sim)) # start new coil block
            out[-1].insert_item(entry[1],entry[0])
            old = entry[0][0]
        return out


    def _connect(self):
        """
        connect to the modbus slave (server)
        """
        if self._sim:
            self.slave = []
            return True
        self.slave = ModbusTcpClient(self._address,self._port)
        status = self.slave.connect()
        if not self._silentMode:
            if status:
                print "connected %s:%d" % (self._address, self._port)
            else:
                print "Failed to connect: %s:%d" % (self._address, self._port)
        return status


    def _disconnect(self):
        """
        close the connection to the modbus slave (server)
        """
        if self._sim:
            return True
        self.slave.close()

    def    request_data(self):
        """

        """
        data = {};
        if not self._connect():
            return False
        for register_block in self._variable_config:
            result = register_block.request_data(self.slave)
            if result is not None:
                data = dict(data.items() + result.items())
            else:
                for name in register_block.variable_name:
                    data[name] = "NaN"
        self._disconnect()
        return data
