# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User

from django.utils import timezone
from django.conf import settings
import time


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



#
# Model
#

class Client(models.Model):
	id 				= models.AutoField(primary_key=True)
	short_name		= models.CharField(max_length=400, default='')
	client_type		= models.CharField(default='generic',choices=settings.PYSCADA_CLIENTS,max_length=400)
	description 	= models.TextField(default='', verbose_name="Description",null=True)
	active			= models.BooleanField(default=True)
	def __unicode__(self):
		return unicode(self.short_name)


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
	client			= models.ForeignKey(Client,null=True, on_delete=models.SET_NULL)
	active			= models.BooleanField(default=True)
	unit 			= models.ForeignKey(UnitConfig,null=True, on_delete=models.SET_NULL)
	writeable		= models.BooleanField(default=False)
	record			= models.BooleanField(default=True)
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
	def __unicode__(self):
		return unicode(self.variable_name)



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
	user	 		= models.ForeignKey(User,null=True, on_delete=models.SET_NULL)

	def __unicode__(self):
		return unicode(self.message)

		
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


