# -*- coding: utf-8 -*-
from pyscada import log
from pyscada.models import Client
from pyscada.models import Variable
from pyscada.hmi.models import HMIVariable
from pyscada.modbus.models import ModbusVariable
from pyscada.modbus.models import ModbusClient
from pyscada.models import Unit
from pyscada.hmi.models import Color
from struct import *

import json
import codecs
import time

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
	`BOOL`								1	1/16 WORD
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
	if variable_class.upper() in ['BOOL']:
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
		# client
		cc, ccc = Client.objects.get_or_create(id = entry['client_id'],defaults={'short_name':entry['client_id'],'description':entry['client_id']})
		# unit config
		uc, ucc = Unit.objects.get_or_create(unit = entry['unit'].replace(' ',''))
		# variable exist
		obj, created = Variable.objects.get_or_create(id=entry['id'],
		defaults={'id':entry['id'],'name':entry['variable_name'].replace(' ',''),'description': entry['description'],'client':cc,'active':bool(entry['active']),'writeable':bool(entry['writeable']),'unit':uc,'value_class':entry["value_class"].replace(' ','')})

		if created:
			log.info(("created variable: %s") %(entry['variable_name']))
		else:
			log.info(("updated variable: %s") %(entry['variable_name']))

			obj.name = entry['variable_name']
			obj.description = entry['description']
			obj.client_id = entry['client_id']
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

def update_client_set(json_data):
	data = json.loads(json_data)
	for entry in data:
		# client
		cc, created = Client.objects.get_or_create(id = entry['client_id'],defaults={'short_name':entry['short_name'],'description':entry['description']})
		if created:
			log.info(("created client: %s") %(entry['short_name']))
		else:
			log.info(("updated client: %s") %(entry['short_name']))
		# modbus config
		if hasattr(cc,'modbusclient'):
			cc.modbusclient.ip_address = entry['modbus_ip.ip_address']
			cc.modbusclient.port = entry['modbus_ip.port']
			cc.modbusclient.protocol = entry['modbus_ip.protocol']
		else:
			ModbusClient(modbus_client=cc,ip_address=entry['modbus_ip.ip_address'],port=entry['modbus_ip.port'],protocol=entry['modbus_ip.protocol'])

def export_xml_config_file(filename=None):
	'''
	export of the Variable Configuration as XML file
	'''
	from xml.dom.minidom import getDOMImplementation
	import sys 
	reload(sys)  
	sys.setdefaultencoding('utf8')
	Meta = {}
	Meta['name'] = ''
	Meta['description'] = ''
	Meta['version'] = '1.0'
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
		# client_id ()
		obj.appendChild(field_('client_id','uint16',item.client_id))
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
	# Client
	for item in Client.objects.all():
		obj = xml_doc.createElement('object')
		obj.setAttribute('name','Client')
		obj.setAttribute('id',item.pk.__str__())
		# name (string)
		obj.appendChild(field_('name','string',item.short_name))
		# description (string)
		obj.appendChild(field_('description','string',item.description))
		# client_type (string)
		obj.appendChild(field_('client_type','string',item.client_type))
		# active (boolean)
		obj.appendChild(field_('active','boolean',item.active))
		if hasattr(item,'modbusclient'):
			# modbus.protocol (string)
			obj.appendChild(field_('modbus.protocol','string',item.modbusclient.protocol_choices[item.modbusclient.protocol][1]))
			# modbus.ip_address (string)
			obj.appendChild(field_('modbus.ip_address','string',item.modbusclient.ip_address))
			# modbus.port (string)
			obj.appendChild(field_('modbus.port','string',item.modbusclient.port))
			# modbus.unit_id (uint8)
			obj.appendChild(field_('modbus.unit_id','uint8',item.modbusclient.unit_id))
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
	_Clients = []
	_Variables = []
	_Units = []
	_Colors = []
	for obj in objects:
		obj_name = obj.getAttribute('name')
		fields = obj.getElementsByTagName('field')
		values = {}
		if not obj.hasAttribute('id'):
			continue
		values['id'] = int(obj.getAttribute('id'))
		for field in fields:
			_parse_field()
		if obj_name.upper() in ['CLIENT']:
			_Clients.append(values)
		elif obj_name.upper() in ['VARIABLE']:
			_Variables.append(values)
		elif obj_name.upper() in ['UNIT']:
			_Units.append(values)
		elif obj_name.upper() in ['COLOR']:
			_Colors.append(values)

	## update/import Clients ###################################################
	for entry in _Clients:
		# Client (object)
		cc, created = Client.objects.get_or_create(pk = entry['id'],defaults={'id':entry['id'],'short_name':entry['name'],'description':entry['description'],'client_type':entry['client_type'],'active':entry['active']})
		if created:
			log.info(("created client: %s") %(entry['name']))
		else:
			cc.short_name = entry['name']
			cc.description = entry['description']
			cc.client_type = entry['client_type']
			cc.active       = entry['active']
			cc.save()
			log.info(("updated client: %s (%d)") %(entry['name'],entry['id']))
		# modbus config
		if entry.has_key('modbus.protocol') and entry.has_key('modbus.ip_address') and entry.has_key('modbus.port') and entry.has_key('modbus.unit_id'):
			# get protocol choice id
			protocol_choices = ModbusClient._meta.get_field('protocol').choices
			for prtc in protocol_choices:
				if entry['modbus.protocol'] == prtc[1]:
					entry['modbus.protocol'] = prtc[0]

			if hasattr(cc,'modbusclient'):
				cc.modbusclient.ip_address = entry['modbus.ip_address']
				cc.modbusclient.port = entry['modbus.port']
				cc.modbusclient.unit_id = entry['modbus.unit_id']
				cc.modbusclient.protocol = entry['modbus.protocol']
				cc.modbusclient.save()
			else:
				ModbusClient(modbus_client=cc,ip_address=entry['modbus.ip_address'],port=entry['modbus.port'],protocol=entry['modbus.protocol'],unit_id=entry['modbus.unit_id'])

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
		defaults={'id':entry['id'],'name':entry['name'],'description': entry['description'],'client_id':entry['client_id'],'active':entry['active'],'writeable':entry['writeable'],'record':entry['record'],'unit_id':entry['unit_id'],'value_class':validate_value_class(entry["value_class"])})

		if created:
			log.info(("created variable: %s") %(entry['name']))
		else:
			log.info(("updated variable: %s") %(entry['name']))

			vc.name = entry['name']
			vc.description = entry['description']
			vc.client_id = entry['client_id']
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
