# -*- coding: utf-8 -*-
from pyscada.models import Log
from time import time
from django.contrib.auth.models import User, Group
	
def add(message,level=0,user=None,message_short=None):
	""" 
	add a new massage/error notice to the log
	<0 - Debug
	1 - Emergency
	2 - Critical
	3 - Errors
	4 - Alerts
	5 - Warnings
	6 - Notification (webnotice)
	7 - Information (webinfo)
	8 - Notification (notice)
	9 - Information (info)
	
	"""
	if message_short is None:
		message_len = len(message)
		if message_len > 35:
			message_short = message[0:31] + '...'
		else:
			message_short = message
		
	log_ob = Log(message=message,level=level,message_short=message_short,timestamp=time())
	if user:
		log_ob.user = user
	log_ob.save()


def debug(message,level=1,user=None,message_short=None):
	add(message,-level,user,message_short)

def emerg(message,user=None,message_short=None):
	add(message,1,user,message_short)

def crit(message,user=None,message_short=None):
	add(message,2,user,message_short)

def error(message,user=None,message_short=None):
	add(message,3,user,message_short)

def alert(message,user=None,message_short=None):
	add(message,4,user,message_short)

def warning(message,user=None,message_short=None):
	add(message,5,user,message_short)

def webnotice(message,user=None,message_short=None):
	add(message,6,user,message_short)	

def webinfo(message,user=None,message_short=None):
	add(message,7,user,message_short)	

def notice(message,user=None,message_short=None):
	add(message,8,user,message_short)	

def info(message,user=None,message_short=None):
	add(message,9,user,message_short)