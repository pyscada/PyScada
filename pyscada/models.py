# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User

from django.utils import timezone
from django.conf import settings
import time
import datetime

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


class Unit(models.Model):
	id 				= models.AutoField(primary_key=True)
	unit			= models.CharField(max_length=80, verbose_name="Unit")
	description 	= models.TextField(default='', verbose_name="Description",null=True)
	udunit			= models.CharField(max_length=500, verbose_name="udUnit")
	def __unicode__(self):
		return unicode(self.unit)
	class  Meta:
		managed=True



class Variable(models.Model):
	id 				= models.AutoField(primary_key=True)
	name 			= models.SlugField(max_length=80, verbose_name="variable name")
	description 	= models.TextField(default='', verbose_name="Description")
	client			= models.ForeignKey(Client,null=True, on_delete=models.SET_NULL)
	active			= models.BooleanField(default=True)
	unit 			= models.ForeignKey(Unit,null=True, on_delete=models.SET_NULL)
	writeable		= models.BooleanField(default=False)
	record			= models.BooleanField(default=True)
	value_class_choices = (('FLOAT32','REAL'),
						('FLOAT32','SINGLE'),
						('FLOAT32','FLOAT32'),
						('FLOAT64','FLOAT'),
						('FLOAT64','FLOAT64'),
						('INT32','INT32'),
						('UINT32','UINT32'),
						('INT16','INT'),
						('INT16','INT16'),
						('UINT16','WORD'),
						('UINT16','UINT'),
						('UINT16','UINT16'),
						('BOOLEAN','BOOL'),
						)
	value_class		= models.CharField(max_length=15, default='FLOAT', verbose_name="value_class",choices=value_class_choices)
	def __unicode__(self):
		return unicode(self.name)



class ClientWriteTask(models.Model):
	id 				= models.AutoField(primary_key=True)
	variable	 	= models.ForeignKey('Variable',null=True, on_delete=models.SET_NULL)
	value			= models.FloatField()
	user	 		= models.ForeignKey(User,null=True, on_delete=models.SET_NULL)
	start 			= models.FloatField(default=0)
	fineshed		= models.FloatField(default=0,blank=True)
	done			= models.BooleanField(default=False,blank=True)
	failed			= models.BooleanField(default=False,blank=True)


class RecordedTime(models.Model):
	id 				= models.AutoField(primary_key=True)
	timestamp 		= models.FloatField()
	def __unicode__(self):
		return unicode(datetime.datetime.fromtimestamp(int(self.timestamp)).strftime('%Y-%m-%d %H:%M:%S'))
	def timestamp_ms(self):
		return self.timestamp * 1000


class RecordedDataFloat(models.Model):
	id          = models.AutoField(primary_key=True)
	value	    = models.FloatField()
	variable	= models.ForeignKey('Variable',null=True, on_delete=models.SET_NULL)
	time		= models.ForeignKey('RecordedTime',null=True, on_delete=models.SET_NULL)
	objects 	= RecordedDataValueManager()
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

class RecordedDataCache(models.Model):
	value	    = models.FloatField()
	variable	= models.OneToOneField('Variable',null=True, on_delete=models.SET_NULL)
	time		= models.ForeignKey('RecordedTime',null=True, on_delete=models.SET_NULL)
	last_change	= models.ForeignKey('RecordedTime',null=True, on_delete=models.SET_NULL,related_name="last_change")
	version		= models.PositiveIntegerField(default=0,null=True,blank=True)
	objects 		= RecordedDataValueManager()
	def __unicode__(self):
		return unicode(self.value)



class Log(models.Model):
	id 				= models.AutoField(primary_key=True)
	level			= models.IntegerField(default=0, verbose_name="level")
	timestamp 		= models.FloatField()
	message_short	= models.CharField(max_length=400, default='', verbose_name="short message")
	message 		= models.TextField(default='', verbose_name="message")
	user	 		= models.ForeignKey(User,null=True, on_delete=models.SET_NULL)

	def __unicode__(self):
		return unicode(self.message)


class BackgroundTask(models.Model):
	id 				= models.AutoField(primary_key=True)
	start 			= models.FloatField(default=0)
	timestamp 		= models.FloatField(default=0)
	progress		= models.FloatField(default=0)
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
	variable	 	= models.ForeignKey(Variable,null=True, on_delete=models.SET_NULL)
	time        	= models.ForeignKey(RecordedTime,null=True, on_delete=models.SET_NULL)
	field_choices 	= ((0,'active'),(1,'writable'),(2,'value_class'),(3,'variable_name'))
	field			= models.PositiveSmallIntegerField(default=0,choices=field_choices)
	old_value		= models.TextField(default='')
	def __unicode__(self):
		return unicode(self.field)

class MailRecipient(models.Model):
	id 				= models.AutoField(primary_key=True)
	subject_prefix  = models.TextField(default='')
	message_suffix	= models.TextField(default='')
	to_email		= models.EmailField(default='')


class Event(models.Model):
	id 				= models.AutoField(primary_key=True)
	label			= models.CharField(max_length=400, default='')
	variable    	= models.ForeignKey(Variable,null=True, on_delete=models.SET_NULL)
	level_choises	= 	(
							(0,'informative'),
							(1,'ok'),
							(2,'warning'),
							(3,'alert'),
						)
	level			= models.PositiveSmallIntegerField(default=0,choices=level_choises)
	fixed_limit		= models.FloatField(default=0,blank=True,null=True)
	variable_limit  = models.ForeignKey(Variable,blank=True,null=True,default=None, on_delete=models.SET_NULL,related_name="variable_limit",help_text="you can choose either an fixed limit or an variable limit that is dependent on the current value of an variable, if you choose a value other then none for varieble limit the fixed limit would be ignored")
	limit_type_choises = 	(
								(0,'value is less than limit',),
								(1,'value is less than or equal to the limit',),
								(2,'value is greater than the limit'),
								(3,'value is greater than or equal to the limit'),
								(4,'value equals the limit'),
							)
	limit_type		= models.PositiveSmallIntegerField(default=0,choices=limit_type_choises)
	action_choises	= 	(
							(0,'just record'),
							(1,'record and send mail'),
							(2,'record, send mail and change variable'),
						)
	action			= models.PositiveSmallIntegerField(default=0,choices=action_choises)
	mail_recipient	= models.ForeignKey(MailRecipient,blank=True,null=True,default=None, on_delete=models.SET_NULL)
	variable_to_change    = models.ForeignKey(Variable,blank=True,null=True,default=None, on_delete=models.SET_NULL,related_name="variable_to_change")
	new_value		= models.FloatField(default=0,blank=True,null=True)
	def _check_limit(self,value):
		'''
		(0,'value is less than limit',),
		(1,'value is less than or equal to the limit',),
		(2,'value is greater than the limit'),
		(3,'value is greater than or equal to the limit'),
		(4,'value equals the limit'),
		'''
		if self.limit_type == 0:
			return value < self.fixed_limit
		elif self.limit_type == 1:
			return value <= self.fixed_limit
		elif self.limit_type == 2:
			return value == self.fixed_limit
		elif self.limit_type == 3:
			return value >= self.fixed_limit
		elif self.limit_type == 4:
			return value > self.fixed_limit
		else:
			return False


	def do_event_check(self,timestamp,value):
		prev_event = RecordedEvent.objects.filter(event=self,active=True)

		if self._check_limit(value):
			if not prev_event:
				prev_event = RecordedEvent(event = self,time_begin=timestamp,active=True)
				prev_event.save()
				return True
		else:
			if prev_event:
				prev_event = prev_event.last()
				prev_event.active = False
				prev_event.time_end = timestamp
				prev_event.save()
		return False





class RecordedEvent(models.Model):
	id          = models.AutoField(primary_key=True)
	event		= models.ForeignKey(Event,null=True, on_delete=models.SET_NULL)
	time_begin  = models.ForeignKey(RecordedTime,null=True, on_delete=models.SET_NULL)
	time_end  	= models.ForeignKey(RecordedTime,null=True, on_delete=models.SET_NULL,related_name="time_end")
	active		= models.BooleanField(default=False,blank=True)
