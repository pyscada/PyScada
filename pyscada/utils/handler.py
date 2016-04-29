#!/usr/bin/python
# -*- coding: utf-8 -*-
from pyscada.models import Device, DeviceWriteTask
from pyscada.models import RecordedTime
from pyscada.models import RecordedDataBoolean, RecordedDataFloat, RecordedDataInt, RecordedDataCache

#from pyscada.__DAQ_Modul__.device import device

from django.conf import settings

from time import time

class Handler:
    def __init__(self):
        '''
        
        '''
        
        self.dt_set = 5 # default value is 5 seconds
        self._devices   = {}    # init device dict
        self._prepare_devices() # 

    def _prepare_devices(self):
        """
        prepare devices for query
        """
        for item in Device.objects.filter(active=1):
            if hasattr(item,'modbusdevice'):
                self._devices[item.pk] = device(item)


    def run(self):
        """
            this function will be called every self._dt seconds
            
            request data
        """
        ## if there is something to write do it 
        self._do_write_task()
        
        ## data acquisition
        timestamp = RecordedTime(timestamp=time())
        timestamp.save()
        data = []
        for idx in self._devices:
            data += self._devices[idx].request_data(timestamp)
        
        return data
    
    
    
    def _do_write_task(self):
        """
        check for write tasks
        """
        
        for task in DeviceWriteTask.objects.filter(done=False,start__lte=time(),failed=False):
            if self._devices.has_key(task.variable.device_id):
                if self._devices[task.variable.device_id].write_data(task.variable.id,task.value):
                    task.done=True
                    task.fineshed=time()
                    task.save()
                    log.notice('changed variable %s (new value %1.6g %s)'%(task.variable.name,task.value,task.variable.unit.description),task.user)
                else:
                    task.failed = True
                    task.fineshed=time()
                    task.save()
                    log.error('change of variable %s failed'%(task.variable.name),task.user)
            else:
                task.failed = True
                task.fineshed=time()
                task.save()
                log.error('device id not valid %d '%(task.variable.device_id),task.user)
