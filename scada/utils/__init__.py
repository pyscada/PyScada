# -*- coding: utf-8 -*-
from scada.utils import modbus
from scada.models import Controllers
from scada.models import ControllerConfig
from scada.models import Variables
from scada.models import InputConfig

def scale_input(Input,scaling):
		sInput = (float(Input)/float(2**scaling.bit))*(scaling.max_value-scaling.min_value)+scaling.min_value
		return sInput

def getClientData(id):
	"""
	getClientData
	"""
	output = {};
	for entries in ControllerConfig.objects.filter(controllers=id):
		output[entries.key] = entries.value;
	return output
	
	
def getActiveClientData():
	"""
	getActiveControllerData
	"""	
	output = [];
	for controller in ControllerConfig.objects.all():
		if Variables.objects.all().filter(active='1',controller=controller.controllers_id).count()!=0:
			output.append(getClientData(controller.controllers_id))
	return output