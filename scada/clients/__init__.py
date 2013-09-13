# -*- coding: utf-8 -*-
from scada import utils

class client():
	def __init__(self):
		self.clients	= {}
		self.clients['modbus_tcpip']	= []
		self.clients['mbus']			= []
		self.variables 	= {}
	
	def __append_key_value(self,array,key,value):
		"""
		
		"""
		key_key = key.split('.')[0]
		attr = key.split('.')[1]
		if array.has_key(key_key):
			array[key_key][attr] = value
		return array		

	
	def _prepare_clients(self):
		"""
		
		"""
		clients = utils.getAllActiveClientSettings()
		for entry in clients:
			for key in entry:
				
				self.clients = self.__append_key_value(self.clients,key,entry[key])
				
				
	def _prepare_variables(self):
		"""
		prepare all variables 
		"""
		
			
	
	
	def request(self):
		"""
		
		"""
		
	