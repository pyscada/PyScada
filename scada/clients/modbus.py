# -*- coding: utf-8 -*-
from pymodbus.client.sync import ModbusTcpClient
from twisted.internet import reactor, protocol

class client:
	"""
	Modbus client (Master) class
	"""
	def __init__(self,address,port,modbus_adr):
		self._address = address
		self._port = port
		self._modbus_adr = modbus_adr
		self.slave = False;

	def _connect():
		"""
		connect to the modbus slave (server)
		"""
		self.slave = ModbusTcpClient(address,port)
    	status = self.slave.connect()
    	if status:
    		print "connected %s:%d" % (address, port)
    	else:
    		print "connection refused %s:%d" % (address, port)
    	return status
    	
	def _disconnect():
		"""
		close the connection to the modbus slave (server)
		"""
		self.slave.close()
		
		
	def	request_data(self):
		"""
		
		"""
		data = [];
		self._connect()
		for entry in self.modbus_adr:
			# entry[0] start_adr
			# entry[1] words_to_read
			result = self.slave.read_input_registers(entry[0],entry[1])
			if hasattr(result, 'registers'):
				data.append(result.registers)
			else:
				data.append(float('NaN'))
		self._disconnect()
		return data
			
			