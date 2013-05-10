# -*- coding: utf-8 -*-


def decode_address(address):
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


