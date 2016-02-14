# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
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

	# def value_class_aware_bulk_create(self,objects):
	# 	pass

#
# Model
#

class Device(models.Model):
	id 				= models.AutoField(primary_key=True)
	short_name		= models.CharField(max_length=400, default='')
	device_type		= models.CharField(default='generic',choices=settings.PYSCADA_DEVICES,max_length=400)
	description 	= models.TextField(default='', verbose_name="Description",null=True)
	active			= models.BooleanField(default=True)
	def __unicode__(self):
		return unicode(self.short_name)


class Unit(models.Model):
	id 				= models.AutoField(primary_key=True)
	unit			= models.CharField(max_length=80, verbose_name="Unit")
	description 	= models.TextField(default='', verbose_name="Description",null=True)
	udunit			= models.CharField(max_length=500, verbose_name="udUnit",default='')
	def __unicode__(self):
		return unicode(self.unit)
	class  Meta:
		managed=True

class Scaling(models.Model):
	id 				= models.AutoField(primary_key=True)
	description 	= models.TextField(default='', verbose_name="Description",null=True,blank=True)
	input_low		= models.FloatField()
	input_high		= models.FloatField()
	output_low		= models.FloatField()
	output_high		= models.FloatField()
	def __unicode__(self):
		if self.description:
			return unicode(self.description)
		else:
			return unicode(str(self.id) + '_[' + str(self.input_low) + ':' + \
					str(self.input_high) + '] -> [' + str(self.output_low) + ':'\
					+ str(self.output_low) + ']')
	def scale_value(self,input_value):
		input_value = float(input_value)
		norm_value = (input_value - self.input_low)/(self.input_high - self.input_low)
		return norm_value * (self.output_high - self.output_low) + self.output_low
	def scale_output_value(self,input_value):
		input_value = float(input_value)
		norm_value = (input_value - self.output_low)/(self.output_high - self.output_low)
		return norm_value * (self.input_high - self.input_low) + self.input_low

class Variable(models.Model):
	id 				= models.AutoField(primary_key=True)
	name 			= models.SlugField(max_length=80, verbose_name="variable name",unique=True)
	description 	= models.TextField(default='', verbose_name="Description")
	device			= models.ForeignKey(Device)
	active			= models.BooleanField(default=True)
	unit 			= models.ForeignKey(Unit,on_delete=models.SET(1))
	writeable		= models.BooleanField(default=False)
	record			= models.BooleanField(default=True)
	value_class_choices = (('FLOAT32','REAL'),
						('FLOAT32','SINGLE'),
						('FLOAT32','FLOAT32'),
						('FLOAT64','LREAL'),
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
						('BOOLEAN','BOOLEAN'),
						)
	scaling			= models.ForeignKey(Scaling,null=True,blank=True, on_delete=models.SET_NULL)
	value_class		= models.CharField(max_length=15, default='FLOAT64', verbose_name="value_class",choices=value_class_choices)
	# for RecodedVariable
	value           	= None
	prev_value 			= None
	store_value 		= False		
	update_timestamp 	= False
	
	def __unicode__(self):
		return unicode(self.name)
	
	def add_attr(self,**kwargs):
		for key in kwargs:
			setattr(self,key,kwargs[key])
	
	def get_bits_by_class(self):
		"""
		`BOOLEAN`							1	1/16 WORD
		`UINT8` `BYTE`						8	1/2 WORD
		`INT8`								8	1/2 WORD
		`UNT16` `WORD`						16	1 WORD
		`INT16`	`INT`						16	1 WORD
		`UINT32` `DWORD`					32	2 WORD
		`INT32`								32	2 WORD
		`FLOAT32` `REAL` `SINGLE` 			32	2 WORD
		`FLOAT64` `LREAL` `FLOAT` `DOUBLE`	64	4 WORD
		"""
		if 	self.value_class.upper() in ['FLOAT64','DOUBLE','FLOAT','LREAL'] :
			return 64
		if 	self.value_class.upper() in ['FLOAT32','SINGLE','INT32','UINT32','DWORD','BCD32','BCD24','REAL'] :
			return 32
		if self.value_class.upper() in ['INT16','INT','WORD','UINT','UINT16','BCD16']:
			return 16
		if self.value_class.upper() in ['INT8','UINT8','BYTE','BCD8']:
			return 8
		if self.value_class.upper() in ['BOOL','BOOLEAN']:
			return 1
		else:
			return 16
	
	
	def update_value(self,value = None,timestamp=None):
		'''
		update the value in the instance and detect value state change
		'''
		
		if self.scaling is None or value is None or self.value_class.upper() in ['BOOL','BOOLEAN']:
			self.value =  value
		else:
			self.value =  self.scaling.scale_value(value)
			#log.notice('%d value %1.3f --> %1.3f'%(self.variable_id,value,self.value))
		self.timestamp = timestamp
		if self.prev_value is None: 
			# no old value in cache 
			self.store_value = True
			self.update_timestamp = False
			self.timestamp_old = self.timestamp
		elif self.value is None:			
			# value could not be queried
			self.store_value = False
			self.update_timestamp = False
		elif self.prev_value == self.value:
			if not self.timestamp_old is None:
				if (self.timestamp.timestamp - self.timestamp_old.timestamp) >= (60*60):
					# store Value if old Value is older then 1 hour
					self.store_value = True
					self.update_timestamp = False
					self.timestamp_old = self.timestamp
				else:
					# value hasn't changed
					self.store_value = False
					self.update_timestamp = True
			else:
				# value hasn't changed
				self.store_value = False
				self.update_timestamp = True
		else:                               
			# value has changed
			self.store_value = True
			self.update_timestamp = False
			self.timestamp_old = self.timestamp
		self.prev_value = self.value
	
	def create_cache_element(self):
		'''
		create a new element to write to cache table
		'''
		if self.store_value and not self.value is None:
			return RecordedDataCache(variable_id=self.pk,value=self.value,time=self.timestamp,last_change = self.timestamp)
		else:
			return None
		
	def create_archive_element(self):
		'''
		create a new element to write to archive table
		'''
		if self.store_value and self.record and not self.value is None:
			if self.value_class.upper() in ['FLOAT','FLOAT64','DOUBLE'] or not self.scaling is None:
				# scaled values will always be stored as float
				return RecordedDataFloat(time=self.timestamp,variable_id=self.pk,value=float(self.value))
			elif self.value_class.upper() in ['FLOAT32','SINGLE','REAL'] :
				return RecordedDataFloat(time=self.timestamp,variable_id=self.pk,value=float(self.value))
			elif  self.value_class.upper() in ['INT32','UINT32','DWORD']:
				return RecordedDataInt(time=self.timestamp,variable_id=self.pk,value=int(self.value))
			elif  self.value_class.upper() in ['WORD','UINT','UINT16']:
				return RecordedDataInt(time=self.timestamp,variable_id=self.pk,value=int(self.value))
			elif  self.value_class.upper() in ['INT16','INT']:
				return RecordedDataInt(time=self.timestamp,variable_id=self.pk,value=int(self.value))
			elif self.value_class.upper() in ['BOOL','BOOLEAN']:
				return RecordedDataBoolean(time=self.timestamp,variable_id=self.pk,value=bool(self.value))
			else:
				return None
		else:
			return None

class DeviceWriteTask(models.Model):
	id 				= models.AutoField(primary_key=True)
	variable	 	= models.ForeignKey('Variable')
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

# class RecordedData(models.Model):
# 	id				= models.BigIntegerField(primary_key=True)
# 	value_boolean   = models.BooleanField(null=True,blank=True)  # boolean
# 	value_int16     = models.SmallIntegerField(null=True,blank=True) # int16, uint8, int8
# 	value_int32     = models.IntegerField(null=True,blank=True)  # uint8, int16, uint16, int32
# 	value_int64     = models.BigIntegerField(null=True,blank=True) # uint32, int64
# 	value_float64 	= models.FloatField(null=True,blank=True) 	 # float64
# 	variable			= models.ForeignKey('Variable')
# 	time			= models.ForeignKey('RecordedTime')
# 	def __unicode__(self):
# 		return unicode(self.value)
# 	def value(self,value_class=None):
# 		'''
# 		return the stored value
# 		'''
# 		if value_class is None:
# 			value_class = self.variable.value_class
# 		
# 		if value_class.upper() in ['FLOAT','FLOAT64','DOUBLE','FLOAT32','SINGLE','REAL']:
# 			return self.value_float64
# 		elif value_class.upper() in ['INT64','UINT32','DWORD']:
# 			return self.value_int64
# 		elif value_class.upper() in ['WORD','UINT','UINT16','INT32']:
# 			return self.value_int32
#       elif value_class.upper() in ['INT16','INT8','UINT8']:
#			return self.value_int16
# 		elif self.value_class.upper() in ['BOOL','BOOLEAN']:
# 			return self.value_boolean
# 		else:
# 			return None


class RecordedDataFloat(models.Model):
	id          = models.AutoField(primary_key=True)
	value	    = models.FloatField()
	variable		= models.ForeignKey('Variable')
	time		= models.ForeignKey('RecordedTime')
	objects 		= RecordedDataValueManager()
	def __unicode__(self):
		return unicode(self.value)

class RecordedDataInt(models.Model):
	id          = models.AutoField(primary_key=True)
	value       = models.BigIntegerField()
	variable    = models.ForeignKey('Variable')
	time        = models.ForeignKey('RecordedTime')
	objects     = RecordedDataValueManager()
	def __unicode__(self):
		return unicode(self.value)

class RecordedDataBoolean(models.Model):
	id          = models.AutoField(primary_key=True)
	value       = models.NullBooleanField()
	variable    = models.ForeignKey('Variable')
	time        = models.ForeignKey('RecordedTime')
	objects     = RecordedDataValueManager()
	def __unicode__(self):
		return unicode(self.value)


class RecordedDataCache(models.Model):
	value	    = models.FloatField()
	variable	= models.OneToOneField('Variable')
	time		= models.ForeignKey('RecordedTime')
	last_change	= models.ForeignKey('RecordedTime',related_name="last_change")
	version		= models.PositiveIntegerField(default=0,null=True,blank=True)
	objects 	= RecordedDataValueManager()
	def __unicode__(self):
		return unicode(self.value)
	def last_update_ms(self):
		return self.time.timestamp * 1000
	def last_change_ms(self):
		return self.last_change * 1000


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
	identifier      = models.CharField(max_length=400, default='',blank=True)

	def __unicode__(self):
		return unicode(self.timestamp)
	def timestamp_ms(self):
		return self.timestamp * 1000


class VariableChangeHistory(models.Model):
	id 				= models.AutoField(primary_key=True)
	variable	 	= models.ForeignKey(Variable)
	time        	= models.ForeignKey(RecordedTime)
	field_choices 	= ((0,'active'),(1,'writable'),(2,'value_class'),(3,'variable_name'))
	field			= models.PositiveSmallIntegerField(default=0,choices=field_choices)
	old_value		= models.TextField(default='')
	def __unicode__(self):
		return unicode(self.field)

class MailRecipient(models.Model):
	id 				= models.AutoField(primary_key=True)
	subject_prefix  = models.TextField(default='',blank=True)
	message_suffix	= models.TextField(default='',blank=True)
	to_email		= models.EmailField(max_length=254)
	def __unicode__(self):
		return unicode(self.to_email)
	
class Event(models.Model):
	id 				= models.AutoField(primary_key=True)
	label			= models.CharField(max_length=400, default='')
	variable    	= models.ForeignKey(Variable)
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
	hysteresis      = models.FloatField(default=0,blank=True)
	action_choises	= 	(
							(0,'just record'),
							(1,'record and send mail only wenn event occurs'),
							(2,'record and send mail'),
							(3,'record, send mail and change variable'),
						)
	action			= models.PositiveSmallIntegerField(default=0,choices=action_choises)
	mail_recipient	= models.ForeignKey(MailRecipient,blank=True,null=True,default=None, on_delete=models.SET_NULL)
	variable_to_change    = models.ForeignKey(Variable,blank=True,null=True,default=None, on_delete=models.SET_NULL,related_name="variable_to_change")
	new_value		= models.FloatField(default=0,blank=True,null=True)
	def __unicode__(self):
		return unicode(self.label)

	def do_event_check(self):
		'''
		
		compair the actual value with the limit value
		
		(0,'value is below the limit',),
		(1,'value is less than or equal to the limit',),
		(2,'value is greater than the limit'),
		(3,'value is greater than or equal to the limit'),
		(4,'value equals the limit'),
		'''
		# 
		# get recorded event
		prev_event = RecordedEvent.objects.filter(event=self,active=True)
		if prev_event:
			prev_value = True
		else:
			prev_value = False
		# get the actual value
		actual_value = RecordedDataCache.objects.filter(variable=self.variable)
		if not actual_value:
			return False
		timestamp = actual_value.last().time
		actual_value = actual_value.last().value
		# determin the limit type, variable or fixed
		if self.variable_limit:
			# item has a variable limit
			# get the limit value
			limit_value = RecordedDataCache.objects.filter(variable=self.variable_limit)
			if not limit_value:
				return False
			if timestamp < limit_value.last().time:
				# wenn limit value has changed after the actual value take that time
				timestamp = limit_value.last().time
			limit_value = limit_value.last().value # get value
		else:
			# item has a fixed limit
			limit_value = self.fixed_limit
	
		if self.limit_type == 0:
			if prev_value:
				limit_check = actual_value < (limit_value + self.hysteresis)
			else:
				limit_check = actual_value < (limit_value - self.hysteresis)
			
			limit_string = 'below the limit'
		elif self.limit_type == 1:
			if prev_value:
				limit_check = actual_value <= (limit_value + self.hysteresis)
			else:
				limit_check = actual_value <= (limit_value - self.hysteresis)
			limit_string = 'below or equals the limit'
		elif self.limit_type == 2:
			limit_check = actual_value <= limit_value + self.hysteresis and actual_value >= limit_value - self.hysteresis
			limit_string = 'equal the limit'
		elif self.limit_type == 3:
			if prev_value:
				limit_check = actual_value >= (limit_value - self.hysteresis)
			else:
				limit_check = actual_value >= (limit_value + self.hysteresis)
			limit_string = 'above or equal the limit'
		elif self.limit_type == 4:
			if prev_value:
				limit_check = actual_value > (limit_value - self.hysteresis)
			else:
				limit_check = actual_value > (limit_value + self.hysteresis)
			limit_string = 'above the limit'
		else:
			return False
		
		# record event
		prev_event = RecordedEvent.objects.filter(event=self,active=True)
		if limit_check: # value is outside of the limit
			if not prev_event:
				# record
				prev_event = RecordedEvent(event = self,time_begin=timestamp,active=True)
				prev_event.save()
				
				# send mail
				if self.limit_type >= 1:
				
					if self.mail_recipient:
						mail_subject = self.mail_recipient.subject_prefix # to do,
						if   self.level == 0: # infomation
							mail_subject += " Infomation "
						elif self.level == 1: # Ok
							mail_subject += " "
						elif self.level == 2: # warning
							mail_subject += " Warning! "	
						elif self.level == 3: # alert
							mail_subject += " Alert! "	
						mail_subject += self.variable.name+" is " + limit_string
						mail_message = "Event " + self.label + " has been triggert\n" 
						mail_message += mail_subject
						mail_message += "Value of " + self.variable.name + " is " + actual_value.__str__() + " " + self.variable.unit.unit
						mail_message += "Limit is " + limit_value.__str__() + " " + self.variable.unit.unit
						mail_message += self.mail_recipient.message_suffix # to do
						mail = Mail(subject = mail_subject, message = mail_message,timestamp = time.time())
						mail.save()
						mail.mail_recipients.add(self.mail_recipient.pk)
						mail.save()
				# do action
				if self.limit_type >= 3:
					
					if self.variable_to_change:
						DeviceWriteTask(variable=self.variable_to_change,value=self.new_value,start=timestamp)
		else: # inside of limit
			if prev_event:
				prev_event = prev_event.last()
				prev_event.active = False
				prev_event.time_end = timestamp
				prev_event.save()
				# send mail
				if self.limit_type >= 2:
				
					if self.mail_recipient:
						mail_subject = self.mail_recipient.subject_prefix # to do,
						if   self.level == 0: # infomation
							mail_subject += " "
						elif self.level == 1: # Ok
							mail_subject += " "
						elif self.level == 2: # warning
							mail_subject += " "	
						elif self.level == 3: # alert
							mail_subject += " "	
							
						mail_message = "  "
						mail_message += self.mail_recipient.message_suffix # to do
						mail = Mail(subject = mail_subject, message = mail_message,timestamp = time.time())
						mail.save()
						mail.mail_recipients.add(self.mail_recipient.pk)
						mail.save()


class RecordedEvent(models.Model):
	id          = models.AutoField(primary_key=True)
	event		= models.ForeignKey(Event)
	time_begin  = models.ForeignKey(RecordedTime)
	time_end  	= models.ForeignKey(RecordedTime,null=True, on_delete=models.SET_NULL,related_name="time_end")
	active		= models.BooleanField(default=False,blank=True)


class Mail(models.Model):
	id 			= models.AutoField(primary_key=True)
	subject     = models.TextField(default='',blank=True)
	message     = models.TextField(default='',blank=True)
	mail_from   = models.TextField(default=settings.EMAIL_FROM,blank=True)
	mail_recipients = models.ManyToManyField(MailRecipient)
	timestamp 	= models.FloatField(default=0,blank=True)
	done		= models.BooleanField(default=False,blank=True)
	send_fail_count = models.PositiveSmallIntegerField(default=0,blank=True)
	def recipients_list(self,exclude_list=[]):
		return [item.to_email for item in self.mail_recipients.exclude(pk__in=exclude_list)]
