# -*- coding: utf-8 -*-
from numpy import float64,float32,int32,uint16,int16,uint8, nan
from pyscada.models import Client
from pyscada.models import Variable
from pyscada.modbus import client as mb
from pyscada import log
from time import time
class client():
    def __init__(self):
        self.clients          = {}
        self.data             = {}
        self.prev_data        = {}
        self._prepare_clients()

    def _prepare_clients(self):
        """
        prepare clients for query
        """
        for item in Client.objects.filter(active=1):
            if hasattr(item,'clientmodbusproperty'):
                self.clients[item.pk] = mb.client(item)


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
       
        self.db_data                = {}
        if not self.data:
            return
        ## set time
        self.db_data['time']        = self.time
        
        for idx in self.clients:
            for var_idx in self.clients[idx].variables:
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
                
                if store_value:
                    self._prepare_db_data(var_idx,self.clients[idx].variables[var_idx]['value_class'],value)

    def write(self,var_idx,value):
        """
        
        """
        var_config = Variable.objects.get(id=var_idx)
        if var_config.writeable:
            return self.clients[var_config.client_id].write_data(var_idx,value)
        else:
            log.error("variable %s is not writable"%var_config.variable_name)
            return False


    def _prepare_db_data(self,var_idx,variable_class,value):
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