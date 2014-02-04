# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import time

#
# Custom field types in here.
#

class UnixTimestampField(models.FloatField):
	"""UnixTimestampField: creates a timestamp field that is represented on the
	database as a double field rather than the usual DATETIME field.
	"""
	def get_db_prep_value(self, value, connection, prepared=False):
		if self.auto_created:
			return  time.time()
		if value==None:
			return None
		return value
		#return time.mktime(value.timetuple())

#
# Manager
#

class RecordedDataValueManager(models.Manager):
	def by_time_id(self,time_id):
		data = super(RecordedDataValueManager, self).get_query_set().filter(time_id=time_id)
		output = {}
		for val in data:
			output[val.variable.variable_name] = val.value()
		return output


class KeyValueManager(models.Manager):
	def get_value_by_key(self,key,**kwargs):
		return super(KeyValueManager, self).get_query_set().get(key=key,**kwargs).value


class VariableConfigManager(models.Manager):
	def get_variable_input_config(self,client_id):
		Variable = super(VariableConfigManager, self).get_query_set().filter(client_id=client_id,active=1)
		variable_config = {}
		for variable in Variable:
			output = {};
			for entry in InputConfig.objects.filter(variable=variable.pk):
				if entry.key.find('.')==-1:
					output[entry.key] = entry.decoded_value()
				else:
					key_key = entry.key.split('.')[0]
					attr = entry.key.split('.')[1]
					if not output.has_key(key_key):
						output[key_key] = {}
					output[key_key][attr] = entry.decoded_value()
			output['variable_name']	= variable.variable_name;
			output['unit']	= variable.unit.unit
			output['class']	= variable.value_class
			variable_config[variable.pk] = output
		return variable_config


class ClientConfigManager(models.Manager):
	def get_client_config(self,client_id):
		config = {}
		for entry in super(ClientConfigManager, self).get_query_set().filter(client_id=client_id):
			if entry.key.find('.')==-1:
				config[entry.key] = entry.decoded_value()
			else:
				key_key = entry.key.split('.')[0]
				attr = entry.key.split('.')[1]
				if not config.has_key(key_key):
					config[key_key] = {}
				config[key_key][attr] = entry.decoded_value()
		config['variable_input_config'] = Variable.objects.get_variable_input_config(client_id)
		return config


	def get_active_client_config(self):
		config = {}
		for entry in Client.objects.filter(active=1):
			if Variable.objects.filter(client_id=entry.pk,active=1).count()>0:
				config[entry.pk] = self.get_client_config(entry.pk)
		return config

#
# Model
#
class GlobalConfig(models.Model):
	id 				= models.AutoField(primary_key=True)
	key 			= models.CharField(max_length=400, default='', verbose_name="key")
	value			= models.CharField(max_length=400, default='', verbose_name="value")
	description 	= models.TextField(default='', verbose_name="Description")
	objects 		= KeyValueManager()

class Client(models.Model):
	id 				= models.AutoField(primary_key=True)
	short_name		= models.CharField(max_length=400, default='')
	description 		= models.TextField(default='', verbose_name="Description")
	active			= models.BooleanField(default=True)
	def __unicode__(self):
		return unicode(self.short_name)

class ClientConfig(models.Model):
	id 				= models.AutoField(primary_key=True)
	client			= models.ForeignKey('Client',null=True, on_delete=models.SET_NULL)
	key_choices		= (("modbus_ip.ip","modbus-IP IP-address"),("modbus_ip.port","modbus-IP port"),)
	key 			= models.CharField(max_length=400, default='', verbose_name="key",choices=key_choices)
	value			= models.CharField(max_length=400, default='', verbose_name="value")
	objects			= KeyValueManager()
	config			= ClientConfigManager()
	def __unicode__(self):
		return unicode(self.value)
	def decoded_value(self):
		if self.value.isdigit():
			return int(self.value)
		return unicode(self.value)


class ScalingConfig(models.Model):
	id 				= models.AutoField(primary_key=True)
	description		= models.CharField(max_length=400, default='', verbose_name="Description")
	min_value		= models.FloatField(default=0, verbose_name="minimal Value")
	max_value		= models.FloatField(default="1", verbose_name="maximal Value")
	bit				= models.PositiveIntegerField(default=0, verbose_name="bit")
	def __unicode__(self):
		return unicode(self.description)


class UnitConfig(models.Model):
	id 				= models.AutoField(primary_key=True)
	unit			= models.CharField(max_length=80, verbose_name="Unit")
	description 		= models.TextField(default='', verbose_name="Description",null=True)
	def __unicode__(self):
		return unicode(self.unit)


class Variable(models.Model):
	id 				= models.AutoField(primary_key=True)
	variable_name 	= models.SlugField(max_length=80, verbose_name="variable name")
	description 		= models.TextField(default='', verbose_name="Description")
	client			= models.ForeignKey('Client',null=True, on_delete=models.SET_NULL)
	active			= models.BooleanField(default=True)
	unit 			= models.ForeignKey('UnitConfig',null=True, on_delete=models.SET_NULL)
	value_class_choices = (('FLOAT32','FLOAT32'),
						('SINGLE','SINGLE'),
						('FLOAT','FLOAT'),
						('FLOAT64','FLOAT64'),
						('REAL','REAL'),
						('INT32','INT32'),
						('UINT32','UINT32'),
						('INT16','INT16'),
						('INT','INT'),
						('WORD','WORD'),
						('UINT','UINT'),
						('UINT16','UINT16'),
						('BOOL','BOOL'),
						)
	
	value_class		= models.CharField(max_length=15, default='FLOAT', verbose_name="value_class",choices=value_class_choices)
	objects			= VariableConfigManager()
	def __unicode__(self):
		return unicode(self.variable_name)


class InputConfig(models.Model):
	id 				= models.AutoField(primary_key=True)
	variable	 		= models.ForeignKey('Variable',null=True, on_delete=models.SET_NULL)
	key_choices 		= (('modbus_ip.address','modbus_ip.address'),)
	key 			= models.CharField(max_length=400, default='', verbose_name="key",choices=key_choices)
	value			= models.CharField(max_length=400, default='', verbose_name="value")
	objects 			= KeyValueManager()
	def __unicode__(self):
		return unicode(self.key)
	def decoded_value(self):
		if self.value.isdigit():
			return int(self.value)
		return unicode(self.value)

class RecordedTime(models.Model):
	id 				= models.AutoField(primary_key=True)
	timestamp 		= models.FloatField()
	def __unicode__(self):
		return unicode(self.timestamp)
	def timestamp_ms(self):
		return self.timestamp * 1000


class RecordedDataFloat(models.Model):
	id            = models.AutoField(primary_key=True)
	value	      = models.FloatField()
	variable	 	= models.ForeignKey('Variable',null=True, on_delete=models.SET_NULL)
	time		= models.ForeignKey('RecordedTime',null=True, on_delete=models.SET_NULL)
	objects 		= RecordedDataValueManager()
	def __unicode__(self):
		return unicode(self.value)

class RecordedDataInt(models.Model):
	id          = models.AutoField(primary_key=True)
	value       = models.IntegerField()
	variable    = models.ForeignKey('Variable',null=True, on_delete=models.SET_NULL)
	time        = models.ForeignKey('RecordedTime',null=True, on_delete=models.SET_NULL)
	objects     = RecordedDataValueManager()
	def __unicode__(self):
		return unicode(self.value)

class RecordedDataBoolean(models.Model):
	id          = models.AutoField(primary_key=True)
	value       = models.NullBooleanField()
	variable    = models.ForeignKey('Variable',null=True, on_delete=models.SET_NULL)
	time        = models.ForeignKey('RecordedTime',null=True, on_delete=models.SET_NULL)
	objects     = RecordedDataValueManager()
	def __unicode__(self):
		return unicode(self.value)


class Log(models.Model):
	id 				= models.AutoField(primary_key=True)
	level			= models.IntegerField(default=0, verbose_name="error level")
	timestamp 		= models.FloatField()
	message_short	= models.CharField(max_length=400, default='', verbose_name="short message")
	message 			= models.TextField(default='', verbose_name="message")
	def __unicode__(self):
		return unicode(self.message)

class WebClientPage(models.Model):
	id 				= models.AutoField(primary_key=True)
	title 			= models.CharField(max_length=400, default='')
	link_title		= models.CharField(max_length=155, default='')
	users			= models.ManyToManyField(User)
	def __unicode__(self):
		return unicode(self.link_title)

class WebClientControlItem(models.Model):
	id 				= models.AutoField(primary_key=True)
	label			= models.CharField(max_length=400, default='')
	position			= models.PositiveSmallIntegerField(default=0)
	type_choices 	= ((0,'label blue'),(1,'label light blue'),(2,'label ok'),(3,'label warning'),(4,'label alarm'),(5,'button default'))
	type			= models.PositiveSmallIntegerField(default=0,choices=type_choices)
	variable    		= models.ForeignKey('Variable',null=True, on_delete=models.SET_NULL)
	users			= models.ManyToManyField(User)
	def __unicode__(self):
		return unicode(self.label+" ("+self.variable.variable_name + ")")

class WebClientChart(models.Model):
	id 				= models.AutoField(primary_key=True)
	label			= models.CharField(max_length=400, default='')
	position			= models.PositiveSmallIntegerField(default=0)
	x_axis_label		= models.CharField(max_length=400, default='',blank=True)
	x_axis_ticks		= models.PositiveSmallIntegerField(default=6)
	y_axis_label		= models.CharField(max_length=400, default='',blank=True)
	y_axis_min		= models.FloatField(default=0)
	y_axis_max		= models.FloatField(default=100)
	size_choices 	= (('pagewidth','page width'),('sidebyside','side by side'))
	size			= models.CharField(max_length=20, default='pagewidth',choices=size_choices)
	variables		= models.ManyToManyField(Variable)
	users			= models.ManyToManyField(User)
	row				= models.ManyToManyField("self",blank=True)
	page			= models.ForeignKey('WebClientPage',null=True, on_delete=models.SET_NULL)
	
	def __unicode__(self):
		return unicode(self.label)
	
class WebClientSlidingPanelMenu(models.Model):
	id 				= models.AutoField(primary_key=True)
	label			= models.CharField(max_length=400, default='')
	position_choices = ((0,'bottom'),(1,'left'),(2,'right'))
	position			= models.PositiveSmallIntegerField(default=0,choices=position_choices)
	items	 	 	= models.ManyToManyField(WebClientControlItem)
	users			= models.ManyToManyField(User)
	def __unicode__(self):
		return unicode(self.label)
		
		
