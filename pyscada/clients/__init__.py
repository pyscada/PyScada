# -*- coding: utf-8 -*-
from numpy import float64,float32,int32,uint16,int16,uint8, nan
from pyscada.models import ClientConfig
from pyscada.clients import modbus as mb
from time import time
class client():
    def __init__(self):
        self.clients        = {}
        self.client_config    = {}
        self.data             = {}
        self.prev_data        = {}
        self._prepare_clients()
        self.backup_data      = {}
    def _prepare_clients(self):
        """
        prepare clients for query
        """
        self.client_config    = ClientConfig.config.get_active_client_config()
        for idx in self.client_config:
            self.clients[idx] = mb.client(self.client_config[idx])


    def request(self):
        """
            request data
        """
        self.prev_data = self.data
        self.data = {}
        # take time
        self.time = time()
        for idx in self.clients:
            self.data[idx] = self.clients[idx].request_data()
            if self.prev_data.has_key(idx):
                if not self.prev_data[idx]:
                    self.prev_data = {}
       
        self.backup_data            = {}
        self.db_data                = {}
        if not self.data:
            return
        ## set time
        self.backup_data['time']    = (float64(self.time)/86400)+719529
        self.db_data['time']        = self.time
        
        for idx in self.clients:
            for var_idx in self.client_config[idx]['variable_input_config']:
                variable_class = self.client_config[idx]['variable_input_config'][var_idx]['class'].replace(' ','')
                name = self.client_config[idx]['variable_input_config'][var_idx]['variable_name']


                store_value = False
                value = 0
                if self.data[idx]:
                    if self.data[idx].has_key(var_idx):
                        if (self.data[idx][var_idx] != None):
                            value = self.data[idx][var_idx]
                            store_value = True
                    
                if store_value:
                    if self.prev_data:
                        if self.prev_data.has_key(idx):
                            if self.prev_data[idx].has_key(var_idx):
                                if value == self.prev_data[idx][var_idx]:
                                    store_value = False
                                elif not store_value:
                                    value = self.prev_data[idx][var_idx]
                
                self._prepare_backup(name,variable_class,value)
                if store_value:
                    self._prepare_save(var_idx,variable_class,value)
                    
    
    def _prepare_backup(self,name,variable_class,value):
        if variable_class.upper() in ['FLOAT','FLOAT64','DOUBLE'] :
            self.backup_data[name] = float64(value)
        elif variable_class.upper() in ['FLOAT32','SINGLE','REAL'] :
            self.backup_data[name] = float32(value)
        elif  variable_class.upper() in ['INT32']:
            self.backup_data[name] = int32(value)
        elif  variable_class.upper() in ['WORD','UINT','UINT16']:
            self.backup_data[name] = uint16(value)    
        elif  variable_class.upper() in ['INT16','INT']:
            self.backup_data[name] = int16(value)
        elif variable_class.upper() in ['BOOL']:
            self.backup_data[name] = uint8(value)
            
    def _prepare_save(self,var_idx,variable_class,value):
        if not self.db_data.has_key(variable_class):
            self.db_data[variable_class.upper()] = {}
        
        if variable_class.upper() in ['FLOAT','FLOAT64','DOUBLE'] :
            self.db_data[variable_class.upper()][var_idx] = float64(value)
        elif variable_class.upper() in ['FLOAT32','SINGLE','REAL'] :
            self.db_data[variable_class.upper()][var_idx] = float32(value)
        elif  variable_class.upper() in ['INT32']:
            self.db_data[variable_class.upper()][var_idx] = int32(value)
        elif  variable_class.upper() in ['WORD','UINT','UINT16']:
           self.db_data[variable_class.upper()][var_idx] = uint16(value)    
        elif  variable_class.upper() in ['INT16','INT']:
            self.db_data[variable_class.upper()][var_idx] = int16(value)
        elif variable_class.upper() in ['BOOL']:
            self.db_data[variable_class.upper()][var_idx] = uint8(value)