# -*- coding: utf-8 -*-
from pyscada.models import Client as Client
from pyscada.models import Variable as Variable
from pyscada.models import BackgroundTask

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.contrib.auth.models import Group

from time import time

class ModbusClient(models.Model):
	modbus_client 		= models.OneToOneField(Client)
	protocol_choices 	= ((0,'TCP'),(1,'UDP'),(2,'serial ASCII'),(3,'serial RTU'),)
	protocol				= models.PositiveSmallIntegerField(default=0,choices=protocol_choices)
	ip_address  			= models.GenericIPAddressField(default='127.0.0.1')
	port				= models.CharField(default='502',max_length=400,help_text="for TCP and UDP enter network port as number (def. 502, for serial ASCII and RTU enter serial port (/dev/pts/13))")
	unit_id				= models.PositiveSmallIntegerField(default=0)
	def __unicode__(self):
		return unicode(self.modbus_client.short_name)

class ModbusVariable(models.Model):
	modbus_variable 				= models.OneToOneField(Variable)
	address  					= models.PositiveIntegerField()
	function_code_read_choices 	= ((0,'not selected'),(1,'coils (FC1)'),(2,'discrete inputs (FC2)'),(3,'holding registers (FC3)'),(4,'input registers (FC4)'))
	function_code_read			= models.PositiveSmallIntegerField(default=0,choices=function_code_read_choices,help_text="")


@receiver(post_save, sender=ModbusClient)
@receiver(post_save, sender=ModbusVariable)
def _reinit_modbus_daemons(sender, **kwargs):
	"""
	update the modbus daemons configuration wenn changes be applied in the model
	"""
	BackgroundTask.objects.filter(label='pyscada.modbus.daemon',done=0,failed=0).update(message='reinit',timestamp = time())
