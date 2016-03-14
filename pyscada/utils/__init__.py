#!/usr/bin/python
# -*- coding: utf-8 -*-
from pyscada import log
from pyscada.models import Device
from pyscada.models import Variable
from pyscada.models import Unit
from pyscada.models import DeviceWriteTask
from pyscada.models import BackgroundTask
from pyscada.models import RecordedTime
from pyscada.models import RecordedDataBoolean, RecordedDataFloat, RecordedDataInt, RecordedDataCache
from pyscada.models import RecordedData
from pyscada.modbus.models import ModbusVariable
from pyscada.modbus.models import ModbusDevice
from pyscada.hmi.models import Color
from pyscada.hmi.models import HMIVariable
from pyscada.hmi.models import Chart
from pyscada.hmi.models import Page
from pyscada.hmi.models import Widget

from django.contrib.auth.models import User
from django.conf import settings

import os
import json
import codecs
import time, datetime
import traceback
from struct import *
import threading


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
		return value[0]

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

def update_variable_set(json_data):
	#json_data = file(json_file)
	#data = json.loads(json_data.read().decode("utf-8-sig"))
	#json_data.close()
	data = json.loads(json_data)
	# deactivate all variables

	for entry in data:
		# device
		cc, ccc = Device.objects.get_or_create(id = entry['device_id'],defaults={'short_name':entry['device_id'],'description':entry['device_id']})
		# unit config
		uc, ucc = Unit.objects.get_or_create(unit = entry['unit'].replace(' ',''))
		# variable exist
		obj, created = Variable.objects.get_or_create(id=entry['id'],
		defaults={'id':entry['id'],'name':entry['variable_name'].replace(' ',''),'description': entry['description'],'device':cc,'active':bool(entry['active']),'writeable':bool(entry['writeable']),'unit':uc,'value_class':entry["value_class"].replace(' ','')})

		if created:
			log.info(("created variable: %s") %(entry['variable_name']))
		else:
			log.info(("updated variable: %s") %(entry['variable_name']))

			obj.name = entry['variable_name']
			obj.description = entry['description']
			obj.device_id = entry['device_id']
			obj.active = bool(entry['active'])
			obj.writeable = bool(entry['writeable'])
			obj.unit = uc
			obj.value_class = entry["value_class"].replace(' ','')
			obj.save()

		if hasattr(obj,'hmivariable'):
			obj.hmivariable.chart_line_color_id = entry["color_id"]
			obj.hmivariable.short_name = entry["short_name"]
			obj.hmivariable.save()
		else:
			HMIVariable(hmi_variable=obj,short_name=entry["short_name"],chart_line_color_id=entry["color_id"]).save()

		if hasattr(obj,'modbusvariable'):
			obj.modbusvariable.address 				= entry["modbus_ip.address"]
			obj.modbusvariable.function_code_read 	= entry["modbus_ip.function_code_read"]
			obj.modbusvariable.save()
		else:
			ModbusVariable(modbus_variable=obj,address=entry["modbus_ip.address"],function_code_read=entry["modbus_ip.function_code_read"]).save()

def update_device_set(json_data):
	data = json.loads(json_data)
	for entry in data:
		# device
		cc, created = Device.objects.get_or_create(id = entry['device_id'],defaults={'short_name':entry['short_name'],'description':entry['description']})
		if created:
			log.info(("created device: %s") %(entry['short_name']))
		else:
			log.info(("updated device: %s") %(entry['short_name']))
		# modbus config
		if hasattr(cc,'modbusdevice'):
			cc.modbusdevice.ip_address = entry['modbus_ip.ip_address']
			cc.modbusdevice.port = entry['modbus_ip.port']
			cc.modbusdevice.protocol = entry['modbus_ip.protocol']
		else:
			ModbusDevice(modbus_device=cc,ip_address=entry['modbus_ip.ip_address'],port=entry['modbus_ip.port'],protocol=entry['modbus_ip.protocol'])

def export_xml_config_file(filename=None):
	'''
	export of the Variable Configuration as XML file
	'''
	from xml.dom.minidom import getDOMImplementation
	import sys
	reload(sys)
	sys.setdefaultencoding('utf8')
	Meta = {}
	if hasattr(settings,'PYSCADA_META'):
		if settings.PYSCADA_META.has_key('description'):
			Meta['description'] = settings.PYSCADA_META['description']
		else:
			Meta['description'] = 'None'
		if settings.PYSCADA_META.has_key('name'):
			Meta['name'] = settings.PYSCADA_META['name']
		else:
			Meta['name'] = 'None'
	else:
		Meta['description'] = 'None'
		Meta['name'] = 'None'
		
	Meta['version'] = '1.1'
	def field_(name,type_,value=None):
		f = xml_doc.createElement('field')
		f.setAttribute('name',name)
		f.setAttribute('type',type_)

		if  type_.upper() in ['STRING','CHAR']:
			if value == '':
				value = ' '
			f.appendChild(xml_doc.createTextNode(value.encode('utf-8')))
		elif type_.upper() in ['BOOLEAN']:
			if value:
				f.appendChild(xml_doc.createTextNode('True'))
			else:
				f.appendChild(xml_doc.createTextNode('False'))
		elif type_.upper() in ['UINT8','UINT16','UINT32','INT8','INT16','INT32','FLOAT64','FLOAT32']:
			f.appendChild(xml_doc.createTextNode(value.__str__()))
		else:
			f.appendChild(xml_doc.createTextNode(' '))
		return f



	impl = getDOMImplementation()
	xml_doc = impl.createDocument(None, "objects", None)
	doc_node = xml_doc.documentElement
	doc_node.setAttribute('version',Meta['version'])
	obj = xml_doc.createElement('object')
	obj.setAttribute('name','Meta')
	# creation_date (string)
	obj.appendChild(field_('creation_date','string',time.strftime('%d-%b-%Y %H:%M:%S')))
	# name (string)
	obj.appendChild(field_('name','string',Meta['name']))
	# description (string)
	obj.appendChild(field_('description','string',Meta['description']))
	doc_node.appendChild(obj)
	
	# Variable (object)
	for item in Variable.objects.all():
		obj = xml_doc.createElement('object')
		obj.setAttribute('name','Variable')
		obj.setAttribute('id',item.pk.__str__())
		# name (string)
		obj.appendChild(field_('name','string',item.name))
		# description (string)
		obj.appendChild(field_('description','string',item.description))
		# active (boolean)
		obj.appendChild(field_('active','boolean',item.active))
		# writeable (boolean)
		obj.appendChild(field_('writeable','boolean',item.writeable))
		# record (boolean)
		obj.appendChild(field_('record','boolean',item.record))
		# value_class (string)
		obj.appendChild(field_('value_class','string',validate_value_class(item.value_class)))
		# device_id ()
		obj.appendChild(field_('device_id','uint16',item.device_id))
		# unit_id
		obj.appendChild(field_('unit_id','uint16',item.unit_id))
		if hasattr(item,'modbusvariable'):
			# modbus.address
			obj.appendChild(field_('modbus.address','uint16',item.modbusvariable.address))
			# modbus.function_code_read
			obj.appendChild(field_('modbus.function_code_read','uint8',item.modbusvariable.function_code_read))
		if hasattr(item,'hmivariable'):
			# hmi.chart_line_color_id
			obj.appendChild(field_('hmi.chart_line_color_id','uint16',item.hmivariable.chart_line_color_id))
			# hmi.short_name
			obj.appendChild(field_('hmi.short_name','string',item.hmivariable.short_name))
			# hmi.chart_line_thickness
			obj.appendChild(field_('hmi.chart_line_thickness','uint8',item.hmivariable.chart_line_thickness))

		# hdf.dims
		obj.appendChild(field_('hdf.dims','uint16',1))
		doc_node.appendChild(obj)
	
	# Unit
	for item in Unit.objects.all():
		obj = xml_doc.createElement('object')
		obj.setAttribute('name','Unit')
		obj.setAttribute('id',item.pk.__str__())
		# unit (string)
		obj.appendChild(field_('unit','string',item.unit))
		# description (string)
		obj.appendChild(field_('description','string',item.description))
		# udunit (string)
		obj.appendChild(field_('udunit','string',item.udunit))
		doc_node.appendChild(obj)
	
	# Device
	for item in Device.objects.all():
		obj = xml_doc.createElement('object')
		obj.setAttribute('name','Device')
		obj.setAttribute('id',item.pk.__str__())
		# name (string)
		obj.appendChild(field_('name','string',item.short_name))
		# description (string)
		obj.appendChild(field_('description','string',item.description))
		# device_type (string)
		obj.appendChild(field_('device_type','string',item.device_type))
		# active (boolean)
		obj.appendChild(field_('active','boolean',item.active))
		if hasattr(item,'modbusdevice'):
			# modbus.protocol (string)
			obj.appendChild(field_('modbus.protocol','string',item.modbusdevice.protocol_choices[item.modbusdevice.protocol][1]))
			# modbus.ip_address (string)
			obj.appendChild(field_('modbus.ip_address','string',item.modbusdevice.ip_address))
			# modbus.port (string)
			obj.appendChild(field_('modbus.port','string',item.modbusdevice.port))
			# modbus.unit_id (uint8)
			obj.appendChild(field_('modbus.unit_id','uint8',item.modbusdevice.unit_id))
		doc_node.appendChild(obj)
	
	# Color
	for item in Color.objects.all():
		obj = xml_doc.createElement('object')
		obj.setAttribute('name','Color')
		obj.setAttribute('id',item.pk.__str__())
		# name (string)
		obj.appendChild(field_('name','string',item.name))
		# R (uint8)
		obj.appendChild(field_('R','uint8',item.R))
		# G (uint8)
		obj.appendChild(field_('G','uint8',item.G))
		# B (uint8)
		obj.appendChild(field_('B','uint8',item.B))
		doc_node.appendChild(obj)
	
	# Chart
	for item in Chart.objects.all():
		obj = xml_doc.createElement('object')
		obj.setAttribute('name','Chart')
		obj.setAttribute('id',item.pk.__str__())
		# name (string)
		obj.appendChild(field_('title','string',item.title))
		# x_axis_label (string)
		obj.appendChild(field_('x_axis_label','string',item.x_axis_label))
		# x_axis_ticks (uint8)
		obj.appendChild(field_('x_axis_ticks','uint8',item.x_axis_ticks))
		# y_axis_label (string)
		obj.appendChild(field_('y_axis_label','string',item.y_axis_label))
		# y_axis_min (float64)
		obj.appendChild(field_('y_axis_min','float64',item.y_axis_min))
		# y_axis_max (float64)
		obj.appendChild(field_('y_axis_max','float64',item.y_axis_max))
		# variables (string)
		variables_list = item.variables_list();
		obj.appendChild(field_('variables','string',str(variables_list)))
		doc_node.appendChild(obj)
	

	if filename:
		with open(filename, "wb") as file_:
			xml_doc.writexml(file_,encoding='utf-8')
	else:
		return xml_doc.toprettyxml(encoding='utf-8')

def import_xml_config_file(filename):
	'''
	read xml file content and write/update the model data
	'''
	from xml.dom.minidom import parse

	with open(filename, "r") as file_:
		xml_doc = parse(file_)
	doc_node       = xml_doc.documentElement
	doc_version    = doc_node.getAttribute('version')
	objects        = doc_node.getElementsByTagName('object')

	def _parse_field():
		if field.hasAttribute('type'):
			_type = field.getAttribute('type')
		else:
			_type = 'string'
		field_name = field.getAttribute('name')
		values[field_name] = _cast(field.firstChild.nodeValue,_type)

	# read all objects
	_Devices = []
	_Variables = []
	_Units = []
	_Colors = []
	_DeviceWriteTask = []
	for obj in objects:
		obj_name = obj.getAttribute('name')
		fields = obj.getElementsByTagName('field')
		values = {}
		if not obj.hasAttribute('id'):
			continue
		values['id'] = int(obj.getAttribute('id'))
		for field in fields:
			_parse_field()
		if obj_name.upper() in ['DEVICE']:
			_Devices.append(values)
		elif obj_name.upper() in ['VARIABLE']:
			_Variables.append(values)
		elif obj_name.upper() in ['UNIT']:
			_Units.append(values)
		elif obj_name.upper() in ['COLOR']:
			_Colors.append(values)
		elif obj_name.upper() in ['DEVICEWRITETASK']:
			_DeviceWriteTask.append(values)

	## update/import Devices ###################################################
	for entry in _Devices:
		# Device (object)
		cc, created = Device.objects.get_or_create(pk = entry['id'],defaults={'id':entry['id'],'short_name':entry['name'],'description':entry['description'],'device_type':entry['device_type'],'active':entry['active']})
		if created:
			log.info(("created device: %s") %(entry['name']))
		else:
			cc.short_name = entry['name']
			cc.description = entry['description']
			cc.device_type = entry['device_type']
			cc.active       = entry['active']
			cc.save()
			log.info(("updated device: %s (%d)") %(entry['name'],entry['id']))
		# modbus config
		if entry.has_key('modbus.protocol') and entry.has_key('modbus.ip_address') and entry.has_key('modbus.port') and entry.has_key('modbus.unit_id'):
			# get protocol choice id
			protocol_choices = ModbusDevice._meta.get_field('protocol').choices
			for prtc in protocol_choices:
				if entry['modbus.protocol'] == prtc[1]:
					entry['modbus.protocol'] = prtc[0]

			if hasattr(cc,'modbusdevice'):
				cc.modbusdevice.ip_address = entry['modbus.ip_address']
				cc.modbusdevice.port = entry['modbus.port']
				cc.modbusdevice.unit_id = entry['modbus.unit_id']
				cc.modbusdevice.protocol = entry['modbus.protocol']
				cc.modbusdevice.save()
			else:
				mc = ModbusDevice(modbus_device=cc,ip_address=entry['modbus.ip_address'],port=entry['modbus.port'],protocol=entry['modbus.protocol'],unit_id=entry['modbus.unit_id'])
				mc.save()
				
	# Unit (object)
	for entry in _Units:
		# unit config
		uc, ucc = Unit.objects.get_or_create(pk = entry['id'],defaults={'id':entry['id'],'unit':entry['unit'],'description':entry['description'],'udunit':entry['udunit']})
		if not created:
			uc.unit = entry['unit']
			uc.description = entry['description']
			uc.udunit = entry['udunit']
			uc.save()

	# Color (object)
	for entry in _Colors:
		# unit config
		cc, ucc = Color.objects.get_or_create(pk = entry['id'],defaults={'id':entry['id'],'name':entry['name'],'R':entry['R'],'G':entry['G'],'B':entry['B']})
		if not created:
			cc.name = entry['name'],
			cc.R = entry['R']
			cc.G = entry['G']
			cc.B = entry['B']
			cc.save()

	# Variable (object)
	for entry in _Variables:
		vc, created = Variable.objects.get_or_create(pk=entry['id'],
		defaults={'id':entry['id'],'name':entry['name'],'description': entry['description'],'device_id':entry['device_id'],'active':entry['active'],'writeable':entry['writeable'],'record':entry['record'],'unit_id':entry['unit_id'],'value_class':validate_value_class(entry["value_class"])})

		if created:
			log.info(("created variable: %s") %(entry['name']))
		else:
			log.info(("updated variable: %s") %(entry['name']))

			vc.name = entry['name']
			vc.description = entry['description']
			vc.device_id = entry['device_id']
			vc.active =entry['active']
			vc.writeable = entry['writeable']
			vc.record = entry['record']
			vc.unit_id = entry['unit_id']
			vc.value_class = validate_value_class(entry["value_class"])
			vc.save()

		if hasattr(vc,'hmivariable'):
			if entry.has_key("hmi.chart_line_color_id"):
				vc.hmivariable.chart_line_color_id = entry["hmi.chart_line_color_id"]
			if entry.has_key("hmi.short_name"):
				vc.hmivariable.short_name = entry["hmi.short_name"]
			if entry.has_key("hmi.chart_line_thickness"):
				vc.hmivariable.chart_line_thickness = entry["hmi.chart_line_thickness"]
			vc.hmivariable.save()
		else:
			if entry.has_key("hmi.chart_line_color_id") and entry.has_key("hmi.short_name") and entry.has_key("hmi.chart_line_thickness"):
				HMIVariable(hmi_variable=vc,short_name=entry["hmi.short_name"],chart_line_color_id=entry["hmi.chart_line_color_id"],chart_line_thickness = entry["hmi.chart_line_thickness"]).save()
				
		if hasattr(vc,'modbusvariable'):
			if entry.has_key("modbus.address"):
				vc.modbusvariable.address 				= entry["modbus.address"]
			if entry.has_key("modbus.function_code_read"):
				vc.modbusvariable.function_code_read 	= entry["modbus.function_code_read"]
			vc.modbusvariable.save()
		else:
			if entry.has_key("modbus.address") and entry.has_key("modbus.function_code_read"):
				ModbusVariable(modbus_variable=vc,address=entry["modbus.address"],function_code_read=entry["modbus.function_code_read"]).save()
				
	for entry in _DeviceWriteTask:
		# start
		if isinstance(entry['start'],basestring):
			# must be convertet from local datestr to datenum
			timestamp = time.mktime(datetime.datetime.strptime(entry['start'], "%d-%b-%Y %H:%M:%S").timetuple())
		else:
			# is already datenum
			timestamp = entry['start']
		# verify timestamp
		if timestamp < time.time():
			continue
		# user
		user = User.objects.filter(username = entry['user'])
		if user:
			user = user.first()
		else:
			user = None
		# variable
		variable = Variable.objects.filter(name=entry['variable'],active=1,device__active=1)
		if variable:
			# check for duplicates
			dcwt = DeviceWriteTask.objects.filter(variable=variable.first(),value=entry['value'],user=user,start__range=(timestamp-2.5,timestamp+2.5))
			if dcwt:
				continue
			# write to DB
			DeviceWriteTask(variable=variable.first(),value=entry['value'],user=user,start=timestamp).save()
			
				
		



def validate_value_class(class_str):
	if 	class_str.upper() in ['FLOAT64','DOUBLE','FLOAT','LREAL']:
		return 'FLOAT64'
	if 	class_str.upper() in ['FLOAT32','SINGLE','REAL']:
		return 'FLOAT32'
	if 	class_str.upper() in ['INT32']:
		return 'INT32'
	if class_str.upper() in ['UINT32','DWORD']:
		return 'UINT32'
	if class_str.upper() in ['INT16','INT']:
		return 'INT16'
	if class_str.upper() in ['UINT','UINT16','WORD']:
		return 'UINT16'
	if class_str.upper() in ['INT8']:
		return 'INT8'
	if class_str.upper() in ['UINT8','BYTE']:
		return 'UINT8'
	if class_str.upper() in ['BOOL','BOOLEAN']:
		return 'BOOLEAN'
	else:
		return 'FLOAT64'

def _cast(value,class_str):
	if 	class_str.upper() in ['FLOAT64','DOUBLE','FLOAT','LREAL','FLOAT32','SINGLE','REAL']:
		return float(value)
	if 	class_str.upper() in ['INT32','UINT32','DWORD','INT16','INT','UINT','UINT16','WORD','INT8','UINT8','BYTE']:
		return int(value)
	if class_str.upper() in ['BOOL','BOOLEAN']:
			return value.lower() == 'true'
	else:
		return value

## daemon
def daemon_run(label,handlerClass):
	pid     = str(os.getpid())

	# init daemon
	
	try:
		mh = handlerClass()
		dt_set = mh.dt_set
	except:
		var = traceback.format_exc()
		log.error("exeption while initialisation of %s:%s %s" % (label,os.linesep, var))
		raise
	# register the task in Backgroudtask list
	bt = BackgroundTask(start=time.time(),label=label,message='daemonized',timestamp=time.time(),pid = pid)
	bt.save()
	bt_id = bt.pk

	# mark the task as running
	bt = BackgroundTask.objects.get(pk=bt_id)
	bt.timestamp = time.time()
	bt.message = 'running...'
	bt.save()

	log.notice("started %s"%label)
	err_count = 0
	# main loop
	while not bt.stop_daemon:
		t_start = time.time()
		if bt.message == 'reinit':
			mh = handlerClass()
			bt = BackgroundTask.objects.get(pk=bt_id)
			bt.timestamp = time.time()
			bt.message = 'running...'
			bt.save()
			log.notice("reinit of %s daemon done"%label)
		try:
			# do actions
			add_recorded_data_to_database(mh.run()) # query data and write to database
			err_count = 0
		except:
			var = traceback.format_exc()
			err_count +=1
			# write log only
			if err_count <= 3 or err_count == 10 or err_count%100 == 0:
				log.debug("occ: %d, exeption in %s daemon%s%s %s" % (err_count,label,os.linesep,os.linesep,var),-1)
			
			# do actions
			mh = handlerClass()
		
		
		# update BackgroudtaskTask
		bt = BackgroundTask.objects.get(pk=bt_id)
		bt.timestamp = time.time()
		if dt_set>0:
			bt.load= max(min((time.time()-t_start)/dt_set,1),0)
		else:
			bt.load= 1
		bt.save()
		dt = dt_set -(time.time()-t_start)
		if dt>0:
			time.sleep(dt)

	## will be called after stop signal
	try:
		bt = BackgroundTask.objects.get(pk=bt_id)
		bt.timestamp = time.time()
		bt.done = True
		bt.message = 'stopped'
		bt.pid = 0
		bt.save()
	except:
		var = traceback.format_exc()
		log.error("exeption while shootdown of %s:%s %s" % (label,os.linesep, var))
	log.notice("stopped %s execution"%label)

def daq_daemon_run(label):
	'''
	aquire data from the different devices/protocols
	'''
	
	
	pid     = str(os.getpid())
	devices = {}
	dt_set  = 2.5
	# init daemons
	for item in Device.objects.exclude(device_type='generic').filter(active=1):
		try:
			tmp_device = item.get_device_instance()
			if tmp_device is not None:
				devices[item.pk] = tmp_device
		except:
			var = traceback.format_exc()
			log.error("exeption while initialisation of %s:%s %s" % (label,os.linesep, var))

	# register the task in Backgroudtask list
	bt = BackgroundTask(start=time.time(),label=label,message='daemonized',timestamp=time.time(),pid = pid)
	bt.save()
	bt_id = bt.pk

	# mark the task as running
	bt = BackgroundTask.objects.get(pk=bt_id)
	bt.timestamp = time.time()
	bt.message = 'running...'
	bt.save()

	log.notice("started %s"%label)
	err_count = 0
	# main loop
	while not bt.stop_daemon:
		t_start = time.time()
		# handle reinit
		if bt.message == 'reinit':
			for item in devices.itervalues():
				item.__init__()
		# process write tasks
		for task in DeviceWriteTask.objects.filter(done=False,start__lte=time.time(),failed=False):
			if not task.variable.scaling is None:
				task.value = task.variable.scaling.scale_output_value(task.value)
			if devices.has_key(task.variable.device_id):
				if devices[task.variable.device_id].write_data(task.variable.id,task.value): # do write task
					task.done=True
					task.fineshed=time.time()
					task.save()
					log.notice('changed variable %s (new value %1.6g %s)'%(task.variable.name,task.value,task.variable.unit.description),task.user)
				else:
					task.failed = True
					task.fineshed=time.time()
					task.save()
					log.error('change of variable %s failed'%(task.variable.name),task.user)
			else:
				task.failed = True
				task.fineshed=time.time()
				task.save()
				log.error('device id not valid %d '%(task.variable.device_id),task.user)
		# add a new timestamp
		timestamp = time.time()
		# start the tasks
		data = [[]]
		for item in devices.itervalues():
			try:
				# do actions
				tmp_data = item.request_data(timestamp) # query data
				if  isinstance(tmp_data,list):
					if len(tmp_data) > 0:
						if len(data[-1])+len(tmp_data) < 998 :
							# add to the last write job
							data[-1] += tmp_data
						else:
							# add to next write job
							data.append(tmp_data)
				err_count = 0
			except:
				var = traceback.format_exc()
				err_count +=1
				# write log only
				if err_count <= 3 or err_count == 10 or err_count%100 == 0:
					log.debug("occ: %d, exeption in %s daemon%s%s %s" % (err_count,label,os.linesep,os.linesep,var),-1)
				# do actions
		
		# write data to the database
		for item in data:
			RecordedData.objects.bulk_create(item)
		# update BackgroudtaskTask
		bt = BackgroundTask.objects.get(pk=bt_id)
		bt.timestamp = time.time()
		if dt_set>0:
			bt.load= max(min((time.time()-t_start)/dt_set,1),0)
		else:
			bt.load= 1
		bt.save()
		dt = dt_set -(time.time()-t_start)
		if dt>0:
			time.sleep(dt)
	## will be called after stop signal
	try:
		bt = BackgroundTask.objects.get(pk=bt_id)
		bt.timestamp = time.time()
		bt.done = True
		bt.message = 'stopped'
		bt.pid = 0
		bt.save()
	except:
		var = traceback.format_exc()
		log.error("exeption while shootdown of %s:%s %s" % (label,os.linesep, var))
	log.notice("stopped %s execution"%label)

def add_recorded_data_to_database(data):
	'''
	takes a list of "RecordData" elements and write them to the Database
	'''
		
	rde = []
	if data:
		RecordedData.objects.bulk_create(data)

			
