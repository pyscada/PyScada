# -*- coding: utf-8 -*-
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