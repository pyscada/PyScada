# -*- coding: utf-8 -*-

import threading
import os,sys
from time import time, localtime, strftime
from pyscada.models import GlobalConfig
from pyscada.clients import client
from pyscada.export.hdf5 import mat
from pyscada.models import RecordedTime
from pyscada.models import RecordedDataFloat
from pyscada.models import RecordedDataInt
from pyscada.models import RecordedDataBoolean

class DataAcquisition():
    def __init__(self):
        self._dt        = GlobalConfig.objects.get_value_by_key('stepsize')
        self._com_dt    = 0
        self._cl        = client()                  # init a client Instance for field data query
        
        
    def run(self):
        dt = time()
       ## second start the query
        self._cl.request();
        if self._cl.db_data:
            self._save_db_data(self._cl.db_data)
        return float(self._dt) -(time()-dt)


    def _save_db_data(self,data):
        """
        save changed values in the database
        """
        dvf = []
        dvi = []
        dvb = []
        timestamp = RecordedTime(timestamp=data.pop('time'))
        timestamp.save()
        for variable_class in data:
            if not data.has_key(variable_class):
                continue
            if not data[variable_class]:
                continue
            for var_idx in data[variable_class]:
                if variable_class.upper() in ['FLOAT32','SINGLE','FLOAT','FLOAT64','REAL'] :
                    dvf.append(RecordedDataFloat(time=timestamp,variable_id=var_idx,value=data[variable_class][var_idx]))
                elif variable_class.upper() in ['INT32','UINT32','INT16','INT','WORD','UINT','UINT16']:
                    dvi.append(RecordedDataInt(time=timestamp,variable_id=var_idx,value=data[variable_class][var_idx]))
                elif variable_class.upper() in ['BOOL']:
                    dvb.append(RecordedDataBoolean(time=timestamp,variable_id=var_idx,value=data[variable_class][var_idx]))
        
        RecordedDataFloat.objects.bulk_create(dvf)
        RecordedDataInt.objects.bulk_create(dvi)
        RecordedDataBoolean.objects.bulk_create(dvb)