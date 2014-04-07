# -*- coding: utf-8 -*-

import threading
import os,sys
from time import time, localtime, strftime
from pyscada.models import GlobalConfig
from pyscada.clients import client
from pyscada.export.hdf5 import mat
from pyscada.models import RecordedDataCache
from pyscada.models import RecordedTime
from pyscada.models import RecordedDataFloat
from pyscada.models import RecordedDataInt
from pyscada.models import RecordedDataBoolean
from pyscada.models import TaskProgress
from pyscada.models import ClientWriteTask
from pyscada import log
import traceback


class DataAcquisition():
    def __init__(self):
        self._dt        = float(GlobalConfig.objects.get_value_by_key('stepsize'))
        self._com_dt    = 0
        self._cl        = client()                  # init a client Instance for field data query
        
    def run(self):
        dt = time()
        ## if there is something to write do it 
        self._do_write_task()
        
        ## second start the query
        self._cl.request()
        if self._cl.db_data:
            self._save_db_data(self._cl.db_data)
        
        return self._dt -(time()-dt)


    def _save_db_data(self,data):
        """
        save changed values in the database
        """
        dvf = []
        dvi = []
        dvb = []
        dvc = []
        del_idx = []
        timestamp = RecordedTime(timestamp=data.pop('time'))
        timestamp.save()
        for variable_class in data:
            if not data.has_key(variable_class):
                continue
            if not data[variable_class]:
                continue
            for var_idx in data[variable_class]:
                dvc.append(RecordedDataCache(variable_id=var_idx,value=data[variable_class][var_idx],time=timestamp,last_change = timestamp))
                del_idx.append(var_idx)
                if variable_class.upper() in ['FLOAT32','SINGLE','FLOAT','FLOAT64','REAL'] :
                    dvf.append(RecordedDataFloat(time=timestamp,variable_id=var_idx,value=data[variable_class][var_idx]))
                elif variable_class.upper() in ['INT32','UINT32','INT16','INT','WORD','UINT','UINT16']:
                    dvi.append(RecordedDataInt(time=timestamp,variable_id=var_idx,value=data[variable_class][var_idx]))
                elif variable_class.upper() in ['BOOL']:
                    dvb.append(RecordedDataBoolean(time=timestamp,variable_id=var_idx,value=data[variable_class][var_idx]))
        
        RecordedDataCache.objects.filter(variable_id__in=del_idx).delete()
        RecordedDataCache.objects.all().update(time=timestamp)
        RecordedDataCache.objects.bulk_create(dvc)
        RecordedDataFloat.objects.bulk_create(dvf)
        RecordedDataInt.objects.bulk_create(dvi)
        RecordedDataBoolean.objects.bulk_create(dvb)
       
    
    
                
                
    
    def _do_write_task(self):
        """
        check for write tasks
        """
        for task in ClientWriteTask.objects.filter(done=False,start__lte=time(),failed=False):
            
            try:
                result = self._cl.write(task.variable_id,task.value)
            except:
                var = traceback.format_exc()
                log.error("exeption in dataaquisition daemnon, %s" % var)
                result = False
                
            if result:
                task.done=True
                task.fineshed=time()
                task.save()
                log.notice('changed variable %s (new value %1.6g %s)'%(task.variable.variable_name,task.value,task.variable.unit.description),task.user)
            else:
                task.failed = True
                task.fineshed=time()
                task.save()
                log.error('change of variable %s failed'%(task.variable.variable_name),task.user)
                