# -*- coding: utf-8 -*-
from pyscada.models import Log
from time import time
	
def add(message,level=0,message_short=None):
	""" 
	add a new massage/error notice to the log
	level 1 info
	level 2 warning
	level 3 error
	level < 0 debug
	
	"""
	if message_short is None:
		message_len = len(message)
		if message_len > 35:
			message_short = message[0:31] + '...'
		else:
			message_short = message
		
	log_ob = Log(message=message,level=level,message_short=message_short,timestamp=time())
	log_ob.save()

def info(message,message_short=None):
	add(message,1,message_short)
	
def error(message,message_short=None):
	add(message,3,message_short)

def warning(message,message_short=None):
	add(message,2,message_short)

def debug(message,level=1,message_short=None):
	add(message,-level,message_short)