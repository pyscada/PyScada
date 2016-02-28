# -*- coding: utf-8 -*-




from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
import time
import datetime


#
## Manager
#

class RecordedDataValueManager(models.Manager):	
	def filter_time(self,time_min=None,time_max=None,**kwargs):
		'''
		
		'''
		if time_min is None:
			time_min = 0
		else:
			time_min = time_min*2097152*1000
		if time_max is None:
			time_max = time.time()*2097152*1000+2097151
		else:
			time_max = time_max*2097152*1000+2097151
		return super(RecordedDataValueManager, self).get_queryset().filter(id__range=(time_min,time_max),**kwargs)
	
	def last_element(self,**kwargs):
		'''
		
		'''
		if kwargs.has_key('time_min'):
			time_min = kwargs.pop('time_min')*2097152*1000
		else:
			time_min = (time.time()-3660)*2097152*1000 # all values will be stored once in a hour
		
		if kwargs.has_key('time_max'):
			time_max = kwargs.pop('time_max')*2097152*1000
		else:
			time_max = time.time()*2097152*1000 # values can't be more recent then now
		
		return super(RecordedDataValueManager, self).get_queryset().filter(\
				id__range=(time_min,time_max),**kwargs).last()
		
			
	def get_values_in_time_range(self,time_min=None,time_max=None,query_first_value=False,time_in_ms=False,key_is_variable_name=False,**kwargs):
		if time_min is None:
			time_min = 0
		else:
			time_min = time_min*2097152*1000
		if time_max is None:
			time_max = time.time()*2097152*1000+2097151
		else:
			time_max = time_max*2097152*1000+2097151
		values = {}
		if kwargs.has_key('variable'):
			return values # just return one value
		elif kwargs.has_key('variable__pk__in'):
			# return all values for the given variables
			variables = Variable.objects.filter(pk__in=kwargs['variable__in'])
		else:
			variables = Variable.objects.all()
		if time_in_ms:
			f_time_scale = 1
		else:
			f_time_scale = 1000
		tmp_time_max = 0           # get the most recent time value
		tmp_time_min = time.time() # 

		# read float32, 64 values
		tmp_vars = variables.filter(\
				value_class__in=('FLOAT','FLOAT64','DOUBLE','FLOAT32','SINGLE','REAL',)\
				).values_list('id',flat=True)
		if tmp_vars:
			tmp = super(RecordedDataValueManager, self).get_queryset().filter(\
				id__range=(time_min,time_max),\
				variable_id__in=tmp_vars\
				).values_list('variable_id','pk','value_float64')
			for item in tmp:
				if not values.has_key(item[0]):
					values[item[0]] = []
				tmp_time = (item[1]-item[0])/(2097152.0*f_time_scale)
				tmp_time_max = max(tmp_time,tmp_time_max)
				tmp_time_min = min(tmp_time,tmp_time_min)
				values[item[0]].append([tmp_time,item[2]]) # time, value
		# read 'INT64','UINT32','DWORD'
		tmp_vars = variables.filter(\
				value_class__in=('INT64','UINT32','DWORD',)\
				).values_list('id',flat=True)
		if tmp_vars:
			tmp = super(RecordedDataValueManager, self).get_queryset().filter(\
				id__range=(time_min,time_max),\
				variable_id__in=tmp_vars\
				).values_list('variable_id','pk','value_int64')
			for item in tmp:
				if not values.has_key(item[0]):
					values[item[0]] = []
				tmp_time = (item[1]-item[0])/(2097152.0*f_time_scale)
				tmp_time_max = max(tmp_time,tmp_time_max)
				tmp_time_min = min(tmp_time,tmp_time_min)
				values[item[0]].append([tmp_time,item[2]]) # time, value
		# read 'WORD','UINT','UINT16','INT32'
		tmp_vars = variables.filter(\
				value_class__in=('WORD','UINT','UINT16','INT32',)\
				).values_list('id',flat=True)
		if tmp_vars:
			tmp = super(RecordedDataValueManager, self).get_queryset().filter(\
				id__range=(time_min,time_max),\
				variable_id__in=tmp_vars\
				).values_list('variable_id','pk','value_int32')
			for item in tmp:
				if not values.has_key(item[0]):
					values[item[0]] = []
				tmp_time = (item[1]-item[0])/(2097152.0*f_time_scale)
				tmp_time_max = max(tmp_time,tmp_time_max)
				tmp_time_min = min(tmp_time,tmp_time_min)
				values[item[0]].append([tmp_time,item[2]]) # time, value
		# read 'INT16','INT8','UINT8'
		tmp_vars = variables.filter(\
				value_class__in=('INT16','INT8','UINT8',)\
				).values_list('id',flat=True)
		if tmp_vars:
			tmp = super(RecordedDataValueManager, self).get_queryset().filter(\
				id__range=(time_min,time_max),\
				variable_id__in=tmp_vars\
				).values_list('variable_id','pk','value_int16')
			for item in tmp:
				if not values.has_key(item[0]):
					values[item[0]] = []
				tmp_time = (item[1]-item[0])/(2097152.0*f_time_scale)
				tmp_time_max = max(tmp_time,tmp_time_max)
				tmp_time_min = min(tmp_time,tmp_time_min)
				values[item[0]].append([tmp_time,item[2]]) # time, value
		# read 'BOOL','BOOLEAN'
		tmp_vars = variables.filter(\
				value_class__in=('BOOL','BOOLEAN',)\
				).values_list('id',flat=True)
		if tmp_vars:
			tmp = super(RecordedDataValueManager, self).get_queryset().filter(\
				id__range=(time_min,time_max),\
				variable_id__in=tmp_vars\
				).values_list('variable_id','pk','value_boolean')
			for item in tmp:
				if not values.has_key(item[0]):
					values[item[0]] = []
				tmp_time = (item[1]-item[0])/(2097152.0*f_time_scale)
				tmp_time_max = max(tmp_time,tmp_time_max)
				tmp_time_min = min(tmp_time,tmp_time_min)
				values[item[0]].append([tmp_time,item[2]]) # time, value
			
		# check if for all variables the first and last value is present
		for key, item in values.iteritems():
			if item[-1][0] < tmp_time_max:
				# append last value
				item.append([tmp_time_max,item[-1][1]])
			if query_first_value and item[0][0] > tmp_time_min:
				# prepend first value
				# item.insert(tmp_time_min,)
				value = super(RecordedDataValueManager, self).get_queryset().filter(\
					id__range=(time_min-(3600*1000*2097152),time_min),\
					variable_id = key).order_by('pk').last()
				if not value is None:
					item.insert(0,[tmp_time_min,value])
		# change the key in the output dict 
		if key_is_variable_name:
			for item in variables:
				if values.has_key(item.pk):
					values[item.name] = values.pop(item.pk)
		
				
		return values
#
## Models
#

class Device(models.Model):
	id 				= models.AutoField(primary_key=True)
	short_name		= models.CharField(max_length=400, default='')
	device_type_choises = (('generic','no Protocol'),('systemstat','Local System Monitoring',),('modbus','Modbus Device',),)
	device_type		= models.CharField(default='generic',choices=device_type_choises,max_length=400)
	description 	= models.TextField(default='', verbose_name="Description",null=True)
	active			= models.BooleanField(default=True)
	def __unicode__(self):
		return unicode(self.short_name)

	def get_device_instance(self):
		from pyscada.modbus.device import Device as ModbusDevice
		from pyscada.systemstat.device import Device as SystemStatDevice
		if self.device_type == 'systemstat':
			return SystemStatDevice(self)
		elif self.device_type == 'modbus' and hasattr(self,'modbusdevice'):
			return ModbusDevice(self)

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
	cov_increment   = models.FloatField(default=0,blank=True)
	# for RecodedVariable
	value           	= None
	prev_value 			= None
	store_value 		= False		
	
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
		self.timestamp = timestamp
		self.store_value = False
		if self.prev_value is None:
			# no prev value in the cache, always store the value
			self.store_value = True
			self.timestamp_old = self.timestamp
		elif self.value is None:
			# value could not be queried
			self.store_value = False
		elif abs(self.prev_value - self.value) < self.cov_increment:
			if self.timestamp_old is not None:
				if (self.timestamp.timestamp - self.timestamp_old.timestamp) >= (60*60):
					# store Value if old Value is older then 1 hour
					self.store_value = True
					self.timestamp_old = self.timestamp
		else:                               
			# value has changed
			self.store_value = True
			self.timestamp_old = self.timestamp
		self.prev_value = self.value
		return self.store_value
	
	def create_recorded_data_element(self):
		'''
		create a new element to write to archive table
		'''
		if self.store_value and not self.value is None:
			return RecordedData(timestamp=self.timestamp,variable=self,value=self.value)
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


class RecordedData(models.Model):
	# Big Int first 42 bis is used for unixtime in ms, unsigt because we only 
	# store time values that are later then 1970, rest 21 bits for the 
	# variable id to have a uniqe primary key
	# 63 bit 111111111111111111111111111111111111111111111111111111111111111
	# 42 bit 111111111111111111111111111111111111111111000000000000000000000
	# 21 bit 										  1000000000000000000000

	id				= models.BigIntegerField(primary_key=True)
	value_boolean   = models.BooleanField(default=False,blank=True)  	# boolean
	value_int16     = models.SmallIntegerField(null=True,blank=True) 	# int16, uint8, int8
	value_int32     = models.IntegerField(null=True,blank=True)  		# uint8, int16, uint16, int32
	value_int64     = models.BigIntegerField(null=True,blank=True) 		# uint32, int64
	value_float64 	= models.FloatField(null=True,blank=True) 	 		# float64
	variable		= models.ForeignKey('Variable')
	objects 		= RecordedDataValueManager()
	
	def __init__(self, *args, **kwargs):
		if kwargs.has_key('timestamp'):
			timestamp = kwargs.pop('timestamp')
		else:
			timestamp = time.time()
		if kwargs.has_key('variable_id'):
			variable_id = kwargs['variable_id']
		elif kwargs.has_key('variable'):
			variable_id = kwargs['variable'].pk
		else:
			variable_id = None
		if not variable_id is None:
			kwargs['id'] = int(int(int(timestamp*1000)*2097152)+variable_id)
		if kwargs.has_key('variable') and kwargs.has_key('value'):
			if kwargs['variable'].value_class.upper() in ['FLOAT','FLOAT64','DOUBLE','FLOAT32','SINGLE','REAL']:
				kwargs['value_float64'] = kwargs.pop('value')
			elif kwargs['variable'].scaling and not kwargs['variable'].value_class.upper() in ['BOOL','BOOLEAN']:
				kwargs['value_float64'] = kwargs.pop('value')
			elif kwargs['variable'].value_class.upper() in ['INT64','UINT32','DWORD']:
				kwargs['value_int64'] = kwargs.pop('value')
			elif kwargs['variable'].value_class.upper() in ['WORD','UINT','UINT16','INT32']:
				kwargs['value_int32'] = kwargs.pop('value')
			elif kwargs['variable'].value_class.upper() in ['INT16','INT8','UINT8']:
				kwargs['value_int16'] = kwargs.pop('value')
			elif kwargs['variable'].value_class.upper() in ['BOOL','BOOLEAN']:
				kwargs['value_boolean'] = kwargs.pop('value')
		# call the django moidel __init__
		super(RecordedData, self).__init__(*args, **kwargs)
		self.timestamp = self.time_value()
				
	def calculate_pk(self,timestamp=None):
		'''
		calculate the primary key from the timestamp in seconds
		'''
		if timestamp is None:
			timestamp = time.time()
		self.pk = int(int(int(timestamp*1000)*2097152)+self.variable.pk)

	def __unicode__(self):
		return unicode(self.value())

	def time_value(self):
		'''
		return the timestamp in seconds calculated from the id
		'''
		return (self.pk-self.variable.pk)/2097152/1000.0 # value in seconds 

	def value(self,value_class=None):
		'''
		return the stored value
		'''
		if value_class is None:
			value_class = self.variable.value_class
		
			
		if value_class.upper() in ['FLOAT','FLOAT64','DOUBLE','FLOAT32','SINGLE','REAL']:
			return self.value_float64
		elif self.variable.scaling and not value_class.upper() in ['BOOL','BOOLEAN']:
			return self.value_float64
		elif value_class.upper() in ['INT64','UINT32','DWORD']:
			return self.value_int64
		elif value_class.upper() in ['WORD','UINT','UINT16','INT32']:
			return self.value_int32
		elif value_class.upper() in ['INT16','INT8','UINT8']:
			return self.value_int16
		elif value_class.upper() in ['BOOL','BOOLEAN']:
			return self.value_boolean
		else:
			return None


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
	variable		= models.ForeignKey('Variable')
	time		= models.ForeignKey('RecordedTime')
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
	def __unicode__(self):
		return unicode(self.value)


class RecordedDataCache(models.Model):
	value	    = models.FloatField()
	variable	= models.OneToOneField('Variable')
	time		= models.ForeignKey('RecordedTime')
	last_change	= models.ForeignKey('RecordedTime',related_name="last_change")
	version		= models.PositiveIntegerField(default=0,null=True,blank=True)
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
	action				= models.PositiveSmallIntegerField(default=0,choices=action_choises)
	mail_recipients		= models.ManyToManyField(User)
	variable_to_change  = models.ForeignKey(Variable,blank=True,null=True,default=None, on_delete=models.SET_NULL,related_name="variable_to_change")
	new_value			= models.FloatField(default=0,blank=True,null=True)
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
		def compose_mail(active):
			if hasattr(settings,'EMAIL_SUBJECT_PREFIX'):
				subject = settings.EMAIL_SUBJECT_PREFIX
			else:
				subject = ''
			
			message = ''
			if active:
				if   self.level == 0: # infomation
					subject += " Infomation "
				elif self.level == 1: # Ok
					subject += " "
				elif self.level == 2: # warning
					subject += " Warning! "	
				elif self.level == 3: # alert
					subject += " Alert! "
				subject += self.variable.name + " has exceeded the limit"
			else:
				subject += " Infomation "
				subject += self.variable.name + " is back in limit"
			message = "The Event " + self.label + " has been triggert\n"
			message += "Value of " + self.variable.name + " is " + actual_value.__str__() + " " + self.variable.unit.unit
			message += " Limit is " + limit_value.__str__() + " " + self.variable.unit.unit
			return (subject,message,)
		# 
		# get recorded event
		prev_event = RecordedEvent.objects.filter(event=self,active=True)
		if prev_event:
			prev_value = True
		else:
			prev_value = False
		# get the actual value
		actual_value = RecordedDataCache.objects.filter(variable=self.variable).last()
		if not actual_value:
			return False
		timestamp = actual_value.time
		actual_value = actual_value.value
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
		elif self.limit_type == 1:
			if prev_value:
				limit_check = actual_value <= (limit_value + self.hysteresis)
			else:
				limit_check = actual_value <= (limit_value - self.hysteresis)
		elif self.limit_type == 2:
			limit_check = actual_value <= limit_value + self.hysteresis and actual_value >= limit_value - self.hysteresis
		elif self.limit_type == 3:
			if prev_value:
				limit_check = actual_value >= (limit_value - self.hysteresis)
			else:
				limit_check = actual_value >= (limit_value + self.hysteresis)
		elif self.limit_type == 4:
			if prev_value:
				limit_check = actual_value > (limit_value - self.hysteresis)
			else:
				limit_check = actual_value > (limit_value + self.hysteresis)
		else:
			return False
		
		# record event
		if limit_check: # value is outside of the limit
			if not prev_event:
				# if there is no previus event record the Event
				prev_event = RecordedEvent(event = self,time_begin=timestamp,active=True)
				prev_event.save()

				if self.limit_type >= 1:
					# compose and send mail
					(subject,message,) = compose_mail(True)
					for recipient in self.mail_recipients.exclude(email=''):
						Mail(None,subject,message,recipient.email,time.time()).save()
				
				if self.limit_type >= 3:
					# do action
					if self.variable_to_change:
						DeviceWriteTask(variable=self.variable_to_change,value=self.new_value,start=timestamp)
		else: # back inside of limit
			if prev_event: # 
				prev_event = prev_event.last()
				prev_event.active = False
				prev_event.time_end = timestamp
				prev_event.save()
				
				if self.limit_type >= 2:
					# compose and send mail
					(subject,message,) = compose_mail(False)
					for recipient in self.mail_recipients.exclude(email=''):
						Mail(None,subject,message,recipient.email,time.time()).save()


class RecordedEvent(models.Model):
	id          = models.AutoField(primary_key=True)
	event		= models.ForeignKey(Event)
	time_begin  = models.FloatField(default=0)
	time_end	= models.FloatField(null=True,blank=True)
	active		= models.BooleanField(default=False,blank=True)


class Mail(models.Model):
	id 			= models.AutoField(primary_key=True)
	subject     = models.TextField(default='',blank=True)
	message     = models.TextField(default='',blank=True)
	to_email	= models.EmailField(max_length=254)
	timestamp 	= models.FloatField(default=0,blank=True)
	done		= models.BooleanField(default=False,blank=True)
	send_fail_count = models.PositiveSmallIntegerField(default=0,blank=True)
	def send_mail(self):
		# TODO check email limit
		# blocked_recipient = [] # list of blocked mail recipoients
		# if settings.PYSCADA.has_key('mail_count_limit'):
		# 	mail_count_limit = float(settings.PYSCADA['mail_count_limit'])
		# else:
		# 	mail_count_limit = 200 # send max 200 Mails per 24h per user
		# 	
		# for recipient in mail.mail_recipients.exclude(to_email__in=blocked_recipient):
		# 	if recipient.mail_set.filter(timestamp__gt=time()-(60*60*24)).count() > self.mail_count_limit:
		# 		blocked_recipient.append(recipient.pk)
		if self.send_fail_count >= 3 or self.done: 
			# only try to send an email three times
			return False
		# send the mail
		if send_mail(self.subject,self.message,settings.DEFAULT_FROM_EMAIL,[self.to_email],fail_silently=True):
			self.done       = True
			self.timestamp  = time.time()
			self.save()
			return True
		else:
			self.send_fail_count = self.send_fail_count + 1
			self.timestamp  = time.time()
			self.save()
			return False
		