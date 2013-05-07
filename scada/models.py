# -*- coding: utf-8 -*-
from django.db import models
import time

class VariableNameManager(models.Manager):
    def get_by_natural_key(self, variable_name, unit):
        return self.get(variable_name=variable_name, unit=unit)

class UnitManager(models.Manager):
    def get_by_natural_key(self, description):
        return self.get(description=description)

class TimeManager(models.Manager):
    def get_by_natural_key(self, timestamp):
        return self.get(timestamp=timestamp)

class InputConfig(models.Model):
	objects 		= VariableNameManager()
	id 				= models.AutoField(primary_key=True)
	variable_name 	= models.SlugField(max_length=80, verbose_name="variable name")
	description 	= models.CharField(max_length=400, default='', verbose_name="Description")
	address			= models.CharField(max_length=8, verbose_name="Address (IW1)")
	number_of_words	= models.PositiveIntegerField(default=1, verbose_name="length")
	controller		= models.ForeignKey('ControllerConfig',null=True, on_delete=models.SET_NULL)
	active			= models.BooleanField()
	unit			= models.ForeignKey("UnitConfig",null=True, on_delete=models.SET_NULL)
	scaling			= models.ForeignKey("ScalingConfig",null=True, on_delete=models.SET_NULL)
	def __unicode__(self):
		return self.variable_name
	def natural_key(self):
		return (self.variable_name,self.unit.natural_key())
	class Meta:
		unique_together = (('variable_name','unit'),)

class ControllerConfig(models.Model):
	id 			= models.AutoField(primary_key=True)
	ip_address 	= models.IPAddressField(default="127.0.0.1", verbose_name="IP Adresse")
	port		= models.PositiveIntegerField(default=502, verbose_name="Port (502)")
	description = models.CharField(max_length=400, default='', verbose_name="Description")
	def __unicode__(self):
		return self.description

class ScalingConfig(models.Model):
	id 			= models.AutoField(primary_key=True)
	description	= models.CharField(max_length=400, default='', verbose_name="Description")
	min_value	= models.FloatField(default=0, verbose_name="minimal Value")	
	max_value	= models.FloatField(default="1", verbose_name="maximal Value")
	bit			= models.PositiveIntegerField(default=0, verbose_name="bit")
	def __unicode__(self):
		return self.description
	
class UnitConfig(models.Model): 
	objects 		= UnitManager()
	unit			= models.CharField(max_length=80, verbose_name="Unit")	
	description 	= models.CharField(max_length=400, default='', verbose_name="Description")
	def __unicode__(self):
		return self.unit
	def natural_key(self):
		return (self.description)

class RecordedTime(models.Model):
	objects 		= TimeManager()
	timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)
	def __unicode__(self):
		return unicode(self.timestamp)
	def natural_key(self):
		return (time.mktime(self.timestamp.timetuple()))	
			
class RecordedData(models.Model): 
	value			= models.FloatField()	
	#Controller		= models.ForeignKey('ControllerConfig',null=True, on_delete=models.SET_NULL)
	variable_name 	= models.ForeignKey('InputConfig',null=True, on_delete=models.SET_NULL)
	time			= models.ForeignKey('RecordedTime',null=True, on_delete=models.SET_NULL)
	def __unicode__(self):
		return unicode(self.value,self.variable_name.variable_name)

class GlobalConfig(models.Model):
	id 				= models.AutoField(primary_key=True)
	key 			= models.SlugField(max_length=400, default='', verbose_name="key")
	value			= models.CharField(max_length=400, default='', verbose_name="value")
	description 	= models.CharField(max_length=400, default='', verbose_name="Description")

class Log(models.Model):
	id 				= models.AutoField(primary_key=True)
	message_id		= models.ForeignKey('MessageIds',null=True, on_delete=models.SET_NULL)
	timestamp 		= models.DateTimeField(auto_now=False, auto_now_add=True)
	message_short	= models.CharField(max_length=400, default='', verbose_name="short message")
	message 		= models.CharField(max_length=800, default='', verbose_name="message")
	
class MessageIds(models.Model):
	id 				= models.PositiveIntegerField(primary_key=True)
	level			= models.PositiveIntegerField(default=0, verbose_name="error level")
	description 	= models.CharField(max_length=600, default='', verbose_name="Description")