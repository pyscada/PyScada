# -*- coding: utf-8 -*-
#from pyscada.utils import modbus
from pyscada.models import Clients
from pyscada.models import ClientConfig
from pyscada.models import Variables
#from pyscada.models import InputConfig
from struct import *


def scale_input(Input,scaling):
		sInput = (float(Input)/float(2**scaling.bit))*(scaling.max_value-scaling.min_value)+scaling.min_value
		return sInput

def decode_float(value):
	"""
	this is a function that convert two UINT values to float value according to the IEEE 7?? specification
	"""
	return unpack('f',pack('2H',value[0],value[1]))[0]

def decode_bcd(values):
	"""
	decode bcd as int to dec
	"""
	binStrOut = ''
	if isinstance(values, (int, long)):
		binStrOut = bin(values)[2:].zfill(16)
		binStrOut = binStrOut[::-1]
	else:
		for value in values:
			binStr = bin(value)[2:].zfill(16)
			binStr = binStr[::-1]
			binStrOut = binStr + binStrOut

	decNum = 0
	print binStrOut
	for i in range(len(binStrOut)/4):
		bcdNum = int(binStrOut[(i*4):(i+1)*4][::-1],2)
		print binStrOut[(i*4):(i+1)*4][::-1]
		if bcdNum>9:
			decNum = -decNum
		else:
			decNum = decNum+(bcdNum*pow(10,i))
		print decNum
	return decNum

def decode_bits(value):
	tmp = [1 if digit=='1' else 0 for digit in bin(value)[2:]]
	while len(tmp)<16:
		tmp.insert(0,0)
	tmp.reverse()
	return tmp

def get_client_settings(client_id):
	"""
	getClientData
	"""
	output = {};
	for entry in ClientConfig.objects.filter(client=client_id):
		key_key = entry.key.split('.')[0]
		attr = entry.key.split('.')[1]
		if output.has_key(key_key)== False:
			output[key_key] = {}
			output[key_key]['variables'] = {}
		output[key_key][attr] = entry.value
	output['id'] = client_id
	output['variables'] = {}
	# add variables
	for entry in Variables.objects.filter(active=1,client=client_id):
		for item in entry.inputconfig_set.values('key','value'):
			key = item['key'].split('.')
			key_key = key[0]
			if len(key)==2:
				attr = item['key'].split('.')[1]
				if output.has_key(key_key):
					if output[key_key]['variables'].has_key(entry.id)==False:
						output[key_key]['variables'][entry.id] = {}
					output[key_key]['variables'][entry.id][attr] = item['value']
			else:
				if output['variables'].has_key(entry.id)==False:
					output['variables'][entry.id] = {}
				output['variables'][entry.id][item['key']] = item['value']
	return output


def get_all_active_clientSettings():
	"""
	getActiveControllerData
	"""
	output = [];
	for client in Clients.objects.all():
		if Variables.objects.filter(active='1',client=client.id).count()!=0:
			output.append(getClientSettings(client.id))
	return output


def get_all_active_variable_settings(client_id):
	output = [];
	for entry in Variables.objects.filter(active='1',client=client_id):
		output.append(getVariableSettings(entry.id))
	return output


def decode_value(value,variable_class):
	if 	variable_class.upper() in ['FLOAT32','SINGLE','FLOAT','REAL']:
		return decode_float(value)
	if 	variable_class.upper() in ['BCD32','BCD24','BCD16']:
		return decode_bcd(values)
	else:
		return value[0]


def get_bits_by_class(variable_class):
	"""
	`BOOL`						1	1/16 WORD
	`UINT8` `BYTE`				8	1/2 WORD
	`INT8`						8	1/2 WORD
	`UNT16` `WORD`				16	1 WORD
	`INT16`						16	1 WORD
	`UINT32` `DWORD`			32	2 WORD
	`INT32`						32	2 WORD
	`FLOAT` `FLOAT32` `SINGLE` 	32	2 WORD
	`FLOAT64` `DOUBLE`			64	4 WORD
	"""
	if 	variable_class.upper() in ['FLOAT64','DOUBLE'] :
		return 64
	if 	variable_class.upper() in ['FLOAT32','SINGLE','FLOAT','INT32','UINT32','DWORD','BCD32','BCD24','REAL'] :
		return 32
	if variable_class.upper() in ['INT16','INT','WORD','UINT','UINT16','BCD16']:
		return 16
	if variable_class.upper() in ['INT8','UINT8','BYTE','BCD8']:
		return 8
	if variable_class.upper() in ['BOOL']:
		return 1
	else:
		return 16