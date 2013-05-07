# -*- coding: utf-8 -*-
import MySQLdb as mdb
import sys
import time
from datetime import timedelta
from datetime import datetime
import threading
from struct import *
from pymodbus.client.sync import ModbusTcpClient as ModbusClient
from twisted.internet import reactor, protocol
from scada.models import InputConfig
from scada.models import ControllerConfig
from scada.models import ScalingConfig
from scada.models import UnitConfig
from scada.models import RecordedData
from scada.models import RecordedTime
from scada.models import GlobalConfig

class lib:
	""" this is a class with tools

	"""
	def decode_modbus_address(self,address):
		""" this function converts address in CoDeSys style to Modbus address
		if the address is already a valid modbus address return this, if not convert
		WAGO        		Modbus      	Access
		%IW0 	- %IW255 	0 		- 255	PLC r / Modbus r                    
		%QW256 	- %QW511    256 	- 511	PLC w / Modbus r                   
		%QW0 	- %QW255    512 	- 767	PLC w / Modbus r     
		%IW256 	- %IW511 	768 	- 1023	PLC r /Modbus w 
		%MW0 	- %MW12287 	12288 	- 24575	PLC rw / Modbus rw
		"""	
		if address[0:2] == 'IW':
			ModAddress = int(address[2:len(address)])
			if (ModAddress < 0 or ModAddress > 511): ModAddress = -1
			if (ModAddress > 255): ModAddress = ModAddress+512
		elif address[0:2] == 'QW':
			ModAddress = int(address[2:len(address)])
			if (ModAddress < 0 or ModAddress > 511): ModAddress = -1
			if (ModAddress < 256): ModAddress = ModAddress+512
		elif address[0:2] == 'MW':
			ModAddress = int(address[2:len(address)])+12288
			if (ModAddress < 12288 or ModAddress > 24575): ModAddress = -1
		else:
			ModAddress = int(address)
			if (ModAddress < 0 or ModAddress > 24575): ModAddress = -1
		return ModAddress
	
	def scale_input(self,Input,scaling):
		sInput = (float(Input)/float(2**scaling.bit))*(scaling.max_value-scaling.min_value)+scaling.min_value
		return sInput

	def decode_modbus_float(self,value):
		""" this is a function to convert two UINT values to float value

		"""
		return unpack('f',pack('2H',value[0],value[1]))[0]
			
class ModbusMaster(lib):
	""" modbus master
	
	"""
	def __init__(self):
		self.lib = lib()
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
		self.controllers = ControllerConfig.objects.all()
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
				address = self.lib.decode_modbus_address(val.address)
				if address <> -1:
					result = self.clients[controller.id].read_input_registers(address,val.number_of_words)
					if hasattr(result, 'registers'):
						if val.number_of_words==2:
							data[idx] = self.lib.scale_input(self.lib.decode_modbus_float(result.registers),val.scaling)
						else:
							data[idx] = self.lib.scale_input(result.registers[0],val.scaling)
					else:
						self.reconnect()
						result = self.clients[controller.id].read_input_registers(address,val.number_of_words)
						if hasattr(result, 'registers'):
							if val.number_of_words==2:
								data[idx] = self.lib.scale_input(self.lib.decode_modbus_float(result.registers),val.scaling)
							else:
								data[idx] = self.lib.scale_input(result.registers[0],val.scaling)
			if len(data)!= 0:
				self.write_data(data,controller)
				
			
