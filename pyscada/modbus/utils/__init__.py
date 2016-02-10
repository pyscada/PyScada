# -*- coding: utf-8 -*-
#from pyscada.utils import modbus
from struct import *


def decode_float(value):
	"""
	this function convert two UINT values to float value according to the IEEE 7?? specification
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




