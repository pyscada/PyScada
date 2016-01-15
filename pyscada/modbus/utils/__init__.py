# -*- coding: utf-8 -*-
#from pyscada.utils import modbus
from struct import *


def scale_input(Input,scaling):
		return (float(Input)/float(2**scaling.bit))*(scaling.max_value-scaling.min_value)+scaling.min_value

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

def decode_value(value,variable_class):
	if 	variable_class.upper() in ['FLOAT32','SINGLE','FLOAT','REAL']:
		return decode_float(value)
	if 	variable_class.upper() in ['BCD32','BCD24','BCD16']:
		return decode_bcd(values)
	else:
		if value:
			return value[0]
		else:
			return None

def encode_float(value):
	"""
	this is a function that convert float values to two UINT value according to the IEEE 7?? specification
	"""
	return unpack('2H',pack('f',float(value)))

def encode_value(value,variable_class):
	if 	variable_class.upper() in ['FLOAT32','SINGLE','FLOAT','REAL']:
		return encode_float(value)
	if 	variable_class.upper() in ['BCD32','BCD24','BCD16']:
		return encode_bcd(values)
	else:
		return value[0]



def get_bits_by_class(variable_class):
	"""
	`BOOLEAN`								1	1/16 WORD
	`UINT8` `BYTE`						8	1/2 WORD
	`INT8`								8	1/2 WORD
	`UNT16` `WORD`						16	1 WORD
	`INT16`	`INT`						16	1 WORD
	`UINT32` `DWORD`					32	2 WORD
	`INT32`								32	2 WORD
	`FLOAT32` `REAL` `SINGLE` 			32	2 WORD
	`FLOAT64` `LREAL` `FLOAT` `DOUBLE`	64	4 WORD
	"""
	if 	variable_class.upper() in ['FLOAT64','DOUBLE','FLOAT','LREAL'] :
		return 64
	if 	variable_class.upper() in ['FLOAT32','SINGLE','INT32','UINT32','DWORD','BCD32','BCD24','REAL'] :
		return 32
	if variable_class.upper() in ['INT16','INT','WORD','UINT','UINT16','BCD16']:
		return 16
	if variable_class.upper() in ['INT8','UINT8','BYTE','BCD8']:
		return 8
	if variable_class.upper() in ['BOOL','BOOLEAN']:
		return 1
	else:
		return 16
