# -*- coding: utf-8 -*-
from django.db import models
import time


class TimeManager(models.Manager):
    def get_by_natural_key(self, timestamp):
        return self.get(timestamp=timestamp)

class GlobalConfig(models.Model):
	id 				= models.AutoField(primary_key=True)
	key 			= models.CharField(max_length=400, default='', verbose_name="key")
	value			= models.CharField(max_length=400, default='', verbose_name="value")
	description 	= models.TextField(default='', verbose_name="Description")


class Controllers(models.Model):
	id 			= models.AutoField(primary_key=True)
	description = models.TextField(default='', verbose_name="Description")
	def __unicode__(self):
		return self.description


class ControllerConfig(models.Model):
	id 				= models.AutoField(primary_key=True)
	controllers		= models.ForeignKey('Controllers',null=True, on_delete=models.SET_NULL)
	key 			= models.CharField(max_length=400, default='', verbose_name="key")
	value			= models.CharField(max_length=400, default='', verbose_name="value")
	def __unicode__(self):
		return self.value


class ScalingConfig(models.Model):
	id 			= models.AutoField(primary_key=True)
	description	= models.CharField(max_length=400, default='', verbose_name="Description")
	min_value	= models.FloatField(default=0, verbose_name="minimal Value")	
	max_value	= models.FloatField(default="1", verbose_name="maximal Value")
	bit			= models.PositiveIntegerField(default=0, verbose_name="bit")
	def __unicode__(self):
		return self.description

	
class UnitConfig(models.Model):
	id 				= models.AutoField(primary_key=True)
	unit			= models.CharField(max_length=80, verbose_name="Unit")	
	description 	= models.TextField(default='', verbose_name="Description")
	def __unicode__(self):
		return self.unit


class Variables(models.Model):
	id 				= models.AutoField(primary_key=True)
	variable_name 	= models.SlugField(max_length=80, verbose_name="variable name")
	description 	= models.TextField(default='', verbose_name="Description")
	controller		= models.ForeignKey('Controllers',null=True, on_delete=models.SET_NULL)
	active			= models.BooleanField()
	def __unicode__(self):
		return self.variable_name


class InputConfig(models.Model):
	id 				= models.AutoField(primary_key=True)
	variable_name 	= models.ForeignKey('Variables',null=True, on_delete=models.SET_NULL)
	key 			= models.CharField(max_length=400, default='', verbose_name="key")
	value			= models.CharField(max_length=400, default='', verbose_name="value")
	def __unicode__(self):
		return self.variable_name


class RecordedTime(models.Model):
	objects 		= TimeManager()
	timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)
	def __unicode__(self):
		return unicode(self.timestamp)
	def natural_key(self):
		return (time.mktime(self.timestamp.timetuple()))	

		
class RecordedDataFloat(models.Model): 
	value			= models.FloatField()	
	variable_name 	= models.ForeignKey('Variables',null=True, on_delete=models.SET_NULL)
	time			= models.ForeignKey('RecordedTime',null=True, on_delete=models.SET_NULL)
	def __unicode__(self):
		return unicode(self.value,self.variable_name.variable_name)


class RecordedDataBoolean(models.Model): 
	value			= models.BooleanField()	
	variable_name 	= models.ForeignKey('Variables',null=True, on_delete=models.SET_NULL)
	time			= models.ForeignKey('RecordedTime',null=True, on_delete=models.SET_NULL)
	def __unicode__(self):
		return unicode(self.value,self.variable_name.variable_name)


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