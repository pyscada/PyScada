#!/usr/bin/python
# -*- coding: utf-8 -*-
from pyscada.models import Client, ClientWriteTask
from pyscada.models import RecordedTime
from pyscada.models import RecordedDataBoolean, RecordedDataFloat, RecordedDataInt, RecordedDataCache

from pyscada.systemstat.client import client

from django.conf import settings

from time import time

class Handler:
    def __init__(self):
        if settings.PYSCADA_SYSTEMSTAT.has_key('polling_interval'):
            self._dt        = float(settings.PYSCADA_SYSTEMSTAT['polling_interval'])
        else:
            self._dt        = 5
        if settings.PYSCADA_SYSTEMSTAT.has_key('polling_interval'):
            self.dt_set = float(settings.PYSCADA_SYSTEMSTAT['polling_interval'])
        else:
            self.dt_set = 5 # default value is 5 seconds
        self._com_dt    = 0
        self._dvf       = []
        self._dvi       = []
        self._dvb       = []
        self._dvc       = []
        self._clients   = {}
        self.data       = {}
        self._prev_data = {}
        self._prepare_clients()
        self.time = []

    def run(self):
        """
            request data
        """
        dt = time()
        self.data = {}
        # take time
        self.time = time()
        for idx in self._clients:
            self.data[idx] = self._clients[idx].request_data()
       
        if not self.data:
            return 
       
        
        self._dvf = []
        self._dvi = []
        self._dvb = []
        self._dvc = []
        del_idx   = []
        upd_idx   = []
        timestamp = RecordedTime(timestamp=self.time)
        timestamp.save()
        for idx in self._clients:
            for var_idx in self._clients[idx].variables:
                
                store_value = False
                value = 0
                if self.data[idx]:
                    if self.data[idx].has_key(var_idx):
                        if (self.data[idx][var_idx] != None):
                            value = self.data[idx][var_idx]
                            store_value = True
                            if self._prev_data.has_key(var_idx):
                                if value == self._prev_data[var_idx]:
                                    store_value = False
                                    
                            self._prev_data[var_idx] = value
                if store_value:
                    self._dvc.append(RecordedDataCache(variable_id=var_idx,value=value,time=timestamp,last_change = timestamp))
                    del_idx.append(var_idx)
                else:
                    upd_idx.append(var_idx)
                            
                if store_value and self._clients[idx].variables[var_idx]['record']:
                    variable_class = self._clients[idx].variables[var_idx]['value_class']
                    if variable_class.upper() in ['FLOAT','FLOAT64','DOUBLE']:
                        self._dvf.append(RecordedDataFloat(time=timestamp,variable_id=var_idx,value=float(value)))
                    elif variable_class.upper() in ['FLOAT32','SINGLE','REAL'] :
                        self._dvf.append(RecordedDataFloat(time=timestamp,variable_id=var_idx,value=float(value)))
                    elif  variable_class.upper() in ['INT32']:
                        self._dvi.append(RecordedDataInt(time=timestamp,variable_id=var_idx,value=int(value)))
                    elif  variable_class.upper() in ['WORD','UINT','UINT16']:
                        self._dvi.append(RecordedDataInt(time=timestamp,variable_id=var_idx,value=int(value)))
                    elif  variable_class.upper() in ['INT16','INT']:
                        self._dvi.append(RecordedDataInt(time=timestamp,variable_id=var_idx,value=int(value)))
                    elif variable_class.upper() in ['BOOL','BOOLEAN']:
                        self._dvb.append(RecordedDataBoolean(time=timestamp,variable_id=var_idx,value=bool(value)))
        
        RecordedDataCache.objects.filter(variable_id__in=del_idx).delete()
        RecordedDataCache.objects.filter(variable_id__in=upd_idx).update(time=timestamp)
        RecordedDataCache.objects.bulk_create(self._dvc)
        
        RecordedDataFloat.objects.bulk_create(self._dvf)
        RecordedDataInt.objects.bulk_create(self._dvi)
        RecordedDataBoolean.objects.bulk_create(self._dvb)
    
    def _prepare_clients(self):
        """
        prepare clients for query
        """
        for item in Client.objects.filter(active=1):
            if item.client_type == 'systemstat':
                self._clients[item.pk] = client(item)