# -*- coding: utf-8 -*-
from scada.utils import modbus
from scada.models import Clients
from scada.models import ClientConfig
from scada.models import Variables
from scada.models import InputConfig
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


def getClientSettings(controller_id):
	"""
	getClientData
	"""
	output = {};
	for entrie in ClientConfig.objects.filter(slients=client_id):
		output[entrie.key] = entrie.value;
	return output

def getVariableSettings(variable_id):
	"""
	
	"""
	output = {};
	for entrie in InputConfig.objects.filter(variable=variable_id):
		output[entrie.key] = entrie.value;
	return output


def getAllActiveClientSettings():
	"""
	getActiveControllerData
	"""	
	output = [];
	for client in ClientConfig.objects.all():
		if Variables.objects.filter(active='1',client=client.client_id).count()!=0:
			output.append(getClientSettings(client.client_id))
	return output

def getAllActiveVariableSettings(controller_id):
	output = [];
	for entrie in Variables.objects.filter(active='1',controller=controller_id):
		output.append(getVariableSettings(entrie.id))
	return output	
		