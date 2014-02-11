# -*- coding: utf-8 -*-
from pyscada.models import Log
from time import time
	
def add(message,level=0,message_short=None):
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
	log_ob.save()


def debug(message,level=1,message_short=None):
	add(message,-level,message_short)

def emerg(message,message_short=None):
	add(message,1,message_short)

def crit(message,message_short=None):
	add(message,2,message_short)

def error(message,message_short=None):
	add(message,3,message_short)

def alert(message,message_short=None):
	add(message,4,message_short)

def warning(message,message_short=None):
	add(message,5,message_short)

def webnotice(message,message_short=None):
	add(message,6,message_short)	

def webinfo(message,message_short=None):
	add(message,7,message_short)	

def notice(message,message_short=None):
	add(message,8,message_short)	

def info(message,message_short=None):
	add(message,9,message_short)
	







