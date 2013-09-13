# -*- coding: utf-8 -*-
from django.db import models
from datetime import datetime
from django.utils import timezone
from time import strftime
import time

#
# Custom field types in here.
#
class UnixTimestampField(models.DateTimeField):
    """UnixTimestampField: creates a DateTimeField that is represented on the
    database as a TIMESTAMP field rather than the usual DATETIME field.
    """
    def __init__(self, null=False, blank=False, **kwargs):
        super(UnixTimestampField, self).__init__(**kwargs)
        # default for TIMESTAMP is NOT NULL unlike most fields, so we have to
        # cheat a little:
        self.blank, self.isnull = blank, null
        self.null = True # To prevent the framework from shoving in "not null".

    def db_type(self, connection):
        typ=['TIMESTAMP']
        # See above!
        if self.isnull:
            typ += ['NULL']
        if self.auto_created:
            typ += ['default CURRENT_TIMESTAMP']
        return ' '.join(typ)

    def get_db_prep_value(self, value, connection, prepared=False):
        if value==None:
            return None
        return strftime('%Y%m%d%H%M%S',value.timetuple())
        #return value

    def to_python(self, value):
        return value

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
	def all(self):
		data = super(RecordedDataValueManager, self).get_query_set().all()
		output = {}
		for val in data:
			if not output.has_key(val.time.natural_key()):
				output[val.time.natural_key()] = {}	
			output[val.time.natural_key()][val.variable.variable_name] = val.value()
		return output
	def later_then(self,timedelta):
		time = timezone.localtime(timezone.now())
		if timedelta.__class__.__name__ == 'timedelta':
			time = time - timedelta
		if timedelta.__class__.__name__ == 'datetime':
			time = timezone.localtime(timedelta)
			
		data = super(RecordedDataValueManager, self).get_query_set().filter(time__timestamp__gt = time)
		output = {}
		for val in data:
			if not output.has_key(val.time.natural_key()):
				output[val.time.natural_key()] = {}	
			output[val.time.natural_key()][val.variable.variable_name] = val.value()
		return output


class KeyValueManager(models.Manager):
	def get_value_by_key(self,key,**kwargs):
		return super(KeyValueManager, self).get_query_set().get(key=key,**kwargs).value


class VariableConfigManager(models.Manager):
	def get_variable_input_config(self,client_id):
		variables = super(VariableConfigManager, self).get_query_set().filter(client_id=client_id,active=1)
		variable_config = {}
		for variable in variables:
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
		config['variable_input_config'] = Variables.objects.get_variable_input_config(client_id)
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

class Clients(models.Model):
	id 				= models.AutoField(primary_key=True)
	description 	= models.TextField(default='', verbose_name="Description")
	
	def __unicode__(self):
		return unicode(self.description)
	def decoded_value(self):
		if self.value.isdigit():
			return int(self.value)
		return unicode(self.value)	

class ClientConfig(models.Model):
	id 				= models.AutoField(primary_key=True)
	client			= models.ForeignKey('Clients',null=True, on_delete=models.SET_NULL)
	key 			= models.CharField(max_length=400, default='', verbose_name="key")
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
	description 	= models.TextField(default='', verbose_name="Description")
	def __unicode__(self):
		return unicode(self.unit)


class Variables(models.Model):
	id 				= models.AutoField(primary_key=True)
	variable_name 	= models.SlugField(max_length=80, verbose_name="variable name")
	description 	= models.TextField(default='', verbose_name="Description")
	client			= models.ForeignKey('Clients',null=True, on_delete=models.SET_NULL)
	active			= models.BooleanField()
	objects			= VariableConfigManager()
	def __unicode__(self):
		return unicode(self.variable_name)


class InputConfig(models.Model):
	id 				= models.AutoField(primary_key=True)
	variable	 	= models.ForeignKey('Variables',null=True, on_delete=models.SET_NULL)
	key 			= models.CharField(max_length=400, default='', verbose_name="key")
	value			= models.CharField(max_length=400, default='', verbose_name="value")
	objects 		= KeyValueManager()
	def __unicode__(self):
		return unicode(self.key)
	def decoded_value(self):
		if self.value.isdigit():
			return int(self.value)
		return unicode(self.value)	

class RecordedTime(models.Model):
	#timestamp 		= models.DateTimeField(auto_now=False, auto_now_add=True,primary_key=True)
	id 				= models.BigIntegerField(primary_key=True)
	timestamp 		= UnixTimestampField(auto_created=True)
	def __unicode__(self):
		return unicode(self.timestamp)
	def natural_key(self):
		return (time.mktime(self.timestamp.timetuple()))

		
class RecordedData(models.Model):
	id 				= models.BigIntegerField(primary_key=True)
	float_value		= models.FloatField(null=True,blank=True)
	int_value		= models.IntegerField(null=True,blank=True)
	uint_value		= models.PositiveIntegerField(null=True,blank=True)
	boolean_value	= models.NullBooleanField(blank=True)
	variable	 	= models.ForeignKey('Variables',null=True, on_delete=models.SET_NULL)
	time			= models.ForeignKey('RecordedTime',null=True, on_delete=models.SET_NULL)
	objects 		= RecordedDataValueManager()
	def value(self):
		if self.float_value is not None:
			return self.float_value
		if 	self.boolean_value is not None:
			return self.boolean_value
		if 	self.int_value is not None:
			return self.int_value
		if 	self.uint_value is not None:
			return self.uint_value

	
	def __unicode__(self):
		if self.float_value is not None:
			return unicode(self.float_value)
		if 	self.boolean_value is not None:
			return unicode(self.boolean_value)
		if 	self.int_value is not None:
			return unicode(self.int_value)
		if 	self.uint_value is not None:
			return unicode(self.uint_value)


class MessageIds(models.Model):
	id 				= models.PositiveIntegerField(primary_key=True)
	level			= models.PositiveIntegerField(default=0, verbose_name="error level")
	description 	= models.TextField(default='', verbose_name="Description")


class Log(models.Model):
	id 				= models.AutoField(primary_key=True)
	message_id		= models.ForeignKey('MessageIds',null=True, on_delete=models.SET_NULL)
	timestamp 		= models.DateTimeField(auto_now=False, auto_now_add=True)
	message_short	= models.CharField(max_length=400, default='', verbose_name="short message")
	message 		= models.TextField(default='', verbose_name="message")


