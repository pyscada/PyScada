# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User, Group
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
		try:
			return super(KeyValueManager, self).get_query_set().get(key=key,**kwargs).value
		except:
			return None


class VariableConfigManager(models.Manager):
	def get_variables_input_config(self,client_id):
		Variables = super(VariableConfigManager, self).get_query_set().filter(client_id=client_id,active=1)
		variables_config = {}
		for variable in Variables:
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
			variables_config[variable.pk] = output
		return variables_config
		
	def get_variable_input_config(self,variable_id):
		variable = super(VariableConfigManager, self).get_query_set().get(id=variable_id)
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
		return output
		

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
		config['variable_input_config'] = Variable.objects.get_variables_input_config(client_id)
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

class Colors(models.Model):
	id 		= models.AutoField(primary_key=True)
	name 	= models.SlugField(max_length=80, verbose_name="variable name")
	R 		= models.PositiveSmallIntegerField(default=0)
	G 		= models.PositiveSmallIntegerField(default=0)
	B 		= models.PositiveSmallIntegerField(default=0)
	def __unicode__(self):
		return unicode('rgb('+str(self.R)+', '+str(self.G)+', '+str(self.B)+', '+')')
	def color_code(self):
		return unicode('#%02x%02x%02x' % (self.R, self.G, self.B))	

class Variable(models.Model):
	id 				= models.AutoField(primary_key=True)
	variable_name 	= models.SlugField(max_length=80, verbose_name="variable name")
	short_name		= models.CharField(default='',max_length=80, verbose_name="variable short name")
	description 		= models.TextField(default='', verbose_name="Description")
	client			= models.ForeignKey('Client',null=True, on_delete=models.SET_NULL)
	active			= models.BooleanField(default=True)
	unit 			= models.ForeignKey('UnitConfig',null=True, on_delete=models.SET_NULL)
	writeable		= models.BooleanField(default=False)
	chart_line_color = models.ForeignKey('Colors',default=0,null=True, on_delete=models.SET_NULL)
	chart_line_thickness_choices = ((3,'3Px'),)
	chart_line_thickness = models.PositiveSmallIntegerField(default=0,choices=chart_line_thickness_choices)
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

class ClientWriteTask(models.Model):
	id 				= models.AutoField(primary_key=True)
	variable	 		= models.ForeignKey('Variable',null=True, on_delete=models.SET_NULL)
	value			= models.FloatField()
	user	 		= models.ForeignKey(User,null=True, on_delete=models.SET_NULL)
	start 			= models.FloatField(default=0)
	fineshed			= models.FloatField(default=0,blank=True)
	done			= models.BooleanField(default=False,blank=True)
	failed			= models.BooleanField(default=False,blank=True)
	

class RecordedTime(models.Model):
	id 				= models.AutoField(primary_key=True)
	timestamp 		= models.FloatField()
	def __unicode__(self):
		return unicode(self.timestamp)
	def timestamp_ms(self):
		return self.timestamp * 1000


class RecordedDataFloat(models.Model):
	id          = models.AutoField(primary_key=True)
	value	    = models.FloatField()
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
	link_title		= models.SlugField(max_length=80, default='')
	groups			= models.ManyToManyField(Group)
	def __unicode__(self):
		return unicode(self.link_title.replace(' ','_'))

class WebClientControlItem(models.Model):
	id 				= models.AutoField(primary_key=True)
	label			= models.CharField(max_length=400, default='')
	position			= models.PositiveSmallIntegerField(default=0)
	type_choices 	= ((0,'label blue'),(1,'label light blue'),(2,'label ok'),(3,'label warning'),(4,'label alarm'),(5,'Control Element'),(6,'Display Value'),)
	type			= models.PositiveSmallIntegerField(default=0,choices=type_choices)
	variable    		= models.ForeignKey('Variable',null=True, on_delete=models.SET_NULL)
	groups			= models.ManyToManyField(Group)
	def __unicode__(self):
		return unicode(self.label+" ("+self.variable.variable_name + ")")
	def web_id(self):
		return unicode(self.id.__str__() + "-" + self.label.replace(' ','_')+"-"+self.variable.variable_name.replace(' ','_'))

class WebClientChart(models.Model):
	id 				= models.AutoField(primary_key=True)
	label			= models.CharField(max_length=400, default='')
	position			= models.PositiveSmallIntegerField(default=0)
	x_axis_label		= models.CharField(max_length=400, default='',blank=True)
	x_axis_ticks		= models.PositiveSmallIntegerField(default=6)
	y_axis_label		= models.CharField(max_length=400, default='',blank=True)
	y_axis_min		= models.FloatField(default=0)
	y_axis_max		= models.FloatField(default=100)
	size_choices 	= (('pagewidth','page width'),('sidebyside','side by side (1/2)'),('sidebyside1','side by side (2/3|1/3)'),)
	size			= models.CharField(max_length=20, default='pagewidth',choices=size_choices)
	variables		= models.ManyToManyField(Variable)
	groups			= models.ManyToManyField(Group)
	row				= models.ManyToManyField("self",blank=True)
	page			= models.ForeignKey('WebClientPage',null=True, on_delete=models.SET_NULL)
	
	def __unicode__(self):
		return unicode(self.label)
	
class WebClientSlidingPanelMenu(models.Model):
	id 				= models.AutoField(primary_key=True)
	label			= models.CharField(max_length=400, default='')
	position_choices = ((0,'Control Menu'),(1,'left'),(2,'right'))
	position			= models.PositiveSmallIntegerField(default=0,choices=position_choices)
	items	 	 	= models.ManyToManyField(WebClientControlItem)
	groups			= models.ManyToManyField(Group)
	def __unicode__(self):
		return unicode(self.label)
		
class TaskProgress(models.Model):
	id 				= models.AutoField(primary_key=True)
	start 			= models.FloatField(default=0)
	timestamp 		= models.FloatField(default=0)
	progress			= models.FloatField(default=0)
	load			= models.FloatField(default=0)
	min 			= models.FloatField(default=0)
	max				= models.FloatField(default=0)
	done			= models.BooleanField(default=False,blank=True)
	failed			= models.BooleanField(default=False,blank=True)
	pid				= models.IntegerField(default=0)
	stop_daemon		= models.BooleanField(default=False,blank=True)
	label			= models.CharField(max_length=400, default='')
	message			= models.CharField(max_length=400, default='')
	
	def __unicode__(self):
		return unicode(self.timestamp)
	def timestamp_ms(self):
		return self.timestamp * 1000


class VariableChangeHistory(models.Model):
	id 				= models.AutoField(primary_key=True)
	variable	 		= models.ForeignKey('Variable',null=True, on_delete=models.SET_NULL)
	time        		= models.ForeignKey('RecordedTime',null=True, on_delete=models.SET_NULL)
	field_choices 	= ((0,'active'),(1,'writable'),(2,'value_class'),(3,'variable_name'))
	field			= models.PositiveSmallIntegerField(default=0,choices=field_choices)
	old_value		= models.TextField(default='')
	def __unicode__(self):
		return unicode(self.field)

class RecordedDataCache(models.Model):
	value	    = models.FloatField()
	variable	 	= models.OneToOneField('Variable',null=True, on_delete=models.SET_NULL)
	time		= models.ForeignKey('RecordedTime',null=True, on_delete=models.SET_NULL)
	objects 		= RecordedDataValueManager()
	def __unicode__(self):
		return unicode(self.value)