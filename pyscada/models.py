# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


#
# Model
#

class Client(models.Model):
	short_name		= models.CharField(max_length=400, default='')
	if hasattr(settings,'PYSCADA_CLIENTS'):
		pyscada_clients = settings.PYSCADA_CLIENTS
	else:
		pyscada_clients = (('modbus','Modbus Client',),)
	client_type		= models.CharField(default='generic',choices=pyscada_clients,max_length=400)
	description 	= models.TextField(default='', verbose_name="Description",null=True)
	active			= models.BooleanField(default=True)
	def __unicode__(self):
		return unicode(self.short_name)


class Unit(models.Model):
	unit			= models.CharField(max_length=80, verbose_name="Unit")
	udUnit			= models.CharField(max_length=80, verbose_name="udUnit representation")
	description 	= models.TextField(default='', verbose_name="Description",null=True)
	def __unicode__(self):
		return unicode(self.unit)



class Variable(models.Model):
	name 			= models.SlugField(max_length=80, verbose_name="variable name")
	description 	= models.TextField(default='', verbose_name="Description")
	client			= models.ForeignKey(Client,null=True, on_delete=models.SET_NULL)
	active			= models.BooleanField(default=True)
	unit 			= models.ForeignKey(Unit,null=True, on_delete=models.SET_NULL)
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
						('BCD32','BCD32'),
						('BCD24','BCD24'),
						('BCD16','BCD16'),
						)
	value_class				= models.CharField(max_length=15, default='FLOAT', verbose_name="value_class",choices=value_class_choices)
	byte_sequence_choises	= 	(
							(0,'1 – 0 – 3 – 2'),
							(1,'0 – 1 – 2 – 3'),
							(2,'2 – 3 – 0 – 1'),
							(3,'3 – 2 – 1 – 0'),
							)
	byte_sequence				= models.PositiveSmallIntegerField(default=0,choices=byte_sequence_choises)
	scaling_active 				= models.BooleanField(default=False)
	scaling_input_value_class 	= models.CharField(max_length=15, default='FLOAT', choices=value_class_choices)
	scaling_input_min 			= models.FloatField(default=0)
	scaling_input_max 			= models.FloatField(default=0)
	scaling_output_min 			= models.FloatField(default=0)
	scaling_output_max 			= models.FloatField(default=0)
	
	def __unicode__(self):
		return unicode(self.name)
	
	def get_value_class_bit_len(self):
		"""
		return the number of bits the data type uses
		
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
		
		if self.scaling_active:
			value_class = self.scaling_input_value_class
		else:
			value_class = self.value_class
		
		if 	value_class.upper() in ['FLOAT64','DOUBLE','FLOAT','LREAL'] :
			return 64
		if 	value_class.upper() in ['FLOAT32','SINGLE','INT32','UINT32','DWORD','BCD32','BCD24','REAL'] :
			return 32
		if value_class.upper() in ['INT16','INT','WORD','UINT','UINT16','BCD16']:
			return 16
		if value_class.upper() in ['INT8','UINT8','BYTE','BCD8']:
			return 8
		if value_class.upper() in ['BOOL']:
			return 1
		else:
			return 16
	
	def scale_value(self,value):
		'''
		scale a given value
		'''
		if not self.scaling_active:
			# if scaling is disabled just return the inputvalue
			return value
		if self.value_class.upper() in ['BOOL'] :
			# don't scale boolean values
			return value
		if (self.scaling_input_max - self.scaling_input_min) == 0:
			# prevent from division by zero
			return value
		
		return  (	(\
						(value - self.scaling_input_min)\
						/ (self.scaling_input_max-self.scaling_input_min)\
											)\
					* (self.scaling_output_max - self.scaling_output_min)\
				) 	+ self.scaling_output_min
	
	def decode_value(self,value):
		if self.scaling_active:
			value_class = self.scaling_input_value_class
		else:
			value_class = self.value_class
		
		if 	value_class.upper() in ['FLOAT32','SINGLE','FLOAT','REAL']:
			# decode Float values
			return unpack('f',pack('2H',value[0],value[1]))[0]
		if 	value_class.upper() in ['BCD32','BCD24','BCD16']:
			# decode bcd as int to dec
			binStrOut = ''
			if isinstance(value, (int, long)):
				binStrOut = bin(value)[2:].zfill(16)
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
		else:
			# for all other value types return the value
			if value:
				return value[0]
			else:
				return None
				
	def encode_value(self,value):
		if self.scaling_active:
			value_class = self.scaling_input_value_class
		else:
			value_class = self.value_class
		if 	value_class.upper() in ['FLOAT32','SINGLE','FLOAT','REAL']:
			return unpack('2H',pack('f',float(value)))
		if 	value_class.upper() in ['BCD32','BCD24','BCD16']:
			return encode_bcd(values)
		else:
			return value[0]


class ClientWriteTask(models.Model):
	variable	 	= models.ForeignKey('Variable',null=True, on_delete=models.SET_NULL)
	value			= models.FloatField()
	user	 		= models.ForeignKey(User,null=True, on_delete=models.SET_NULL)
	start 			= models.FloatField(default=0)
	fineshed		= models.FloatField(default=0,blank=True)
	done			= models.BooleanField(default=False,blank=True)
	failed			= models.BooleanField(default=False,blank=True)

class RecordedDataCache(models.Model):
	id			= models.BigIntegerField(primary_key=True) 
	float_value	= models.FloatField(default=None,blank=True,null=True,) # for all float types
	int_value	= models.BigIntegerField(default=None,blank=True,null=True,) # for all intger types e.g. bool, uint8-32, int8-64 
	variable	= models.ForeignKey('Variable',null=True, on_delete=models.SET_NULL)
	last_update	= models.FloatField()
	last_change	= models.FloatField()
	def __unicode__(self):
		return unicode(self.value())
	def last_update_ms(self):
		return self.last_update * 1000
	def last_change_ms(self):
		return self.last_change * 1000
	def value(self):
		if self.int_value != None:
			return self.int_value
		else:
			return self.float_value
		

class Log(models.Model):
	level			= models.IntegerField(default=0, verbose_name="level")
	timestamp 		= models.FloatField()
	message_short	= models.CharField(max_length=400, default='', verbose_name="short message")
	message 		= models.TextField(default='', verbose_name="message")
	user	 		= models.ForeignKey(User,null=True, on_delete=models.SET_NULL)

	def __unicode__(self):
		return unicode(self.message)

		
class BackgroundTask(models.Model):
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



class MailRecipient(models.Model):
	subject_prefix  = models.TextField(default='')
	message_suffix	= models.TextField(default='')
	to_email		= models.EmailField(default='')
	
	
class Event(models.Model):
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
	event		= models.ForeignKey(Event,null=True, on_delete=models.SET_NULL)
	time_begin  = models.FloatField()
	time_end  	= models.FloatField()
	active		= models.BooleanField(default=False,blank=True)

class BackupFile(models.Model):
	file 		= models.FileField()
	time_begin  = models.FloatField()
	time_end  	= models.FloatField()
	active		= models.BooleanField(default=False,blank=True)
	
