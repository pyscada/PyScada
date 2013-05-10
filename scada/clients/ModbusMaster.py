# -*- coding: utf-8 -*-
import sys
import time
from datetime import timedelta
from datetime import datetime
from pymodbus.client.sync import ModbusTcpClient as ModbusClient
from twisted.internet import reactor, protocol
from scada.models import InputConfig
from scada.models import ControllerConfig
from scada.models import ScalingConfig
from scada.models import UnitConfig
from scada.models import RecordedDataFloat
from scada.models import RecordedDataBoolean
from scada.models import RecordedTime
from scada.models import GlobalConfig
from scada import utils


class ModbusMaster():
    """ 
    modbus master
    
    """
    def __init__(self):
    	self.controllers = ControllerConfig.objects.all()
    	self.variables = {}
    	self.clients = {}
    	self.reconnect()
    	self.time = 0;
    	print "init done"
    
    def get_variable_data(self,controller):
    	self.variables[controller.id] = InputConfig.objects.filter(controller=controller.id,active=1)
    
    def write_data(self,data,controller):
    	for idx, val in enumerate(self.variables[controller.id]):
    		if data.has_key(idx):
    			DataToRecord = RecordedData(value = data[idx],variable_name=val,time=self.time)
    			DataToRecord.save()
    
    
    def reconnect(self):
    	self.controllers = Controllers.objects.all()
    	for controller in self.controllers:
    		self.get_variable_data(controller)
    		if len(self.variables[controller.id])!=0:
    			self.clients[controller.id] = self.connect(controller.ip_address,int(controller.port))
    
    def disconnect(self):
    	for client in self.clients:
    		client.close()
    		
    def connect(self,address,port):
    	client = ModbusClient(address,port)
    	OK = client.connect()
    	if OK:
    		print "connected %s:%d" % (address, port)
    	else:
    		print "connection refused %s:%d" % (address, port)
    	return 	client
    
    def request(self):
    	OK = 1
    	variablesDict = {}
    	self.time = RecordedTime()
    	self.time.save()
    	for controller in self.controllers:
    		data = {}
    		for idx, val in enumerate(self.variables[controller.id]):
    			address = utils.modbus.decode_address(val.address)
    			if address <> -1:
    				result = self.clients[controller.id].read_input_registers(address,val.number_of_words)
    				if hasattr(result, 'registers'):
    					if val.number_of_words==2:
    						data[idx] = utils.scale_input(utils.modbus.decode_float(result.registers),val.scaling)
    					else:
    						data[idx] = utils.scale_input(result.registers[0],val.scaling)
    				else:
    					self.reconnect()
    					result = self.clients[controller.id].read_input_registers(address,val.number_of_words)
    					if hasattr(result, 'registers'):
    						if val.number_of_words==2:
    							data[idx] = utils.scale_input(utils.modbus.decode_float(result.registers),val.scaling)
    						else:
    							data[idx] = utils.scale_input(result.registers[0],val.scaling)
    		if len(data)!= 0:
    			self.write_data(data,controller)
			
			