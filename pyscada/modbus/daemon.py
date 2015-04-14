#!/usr/bin/python
# -*- coding: utf-8 -*- 
from pyscada import log
from pyscada.modbus import client
from pyscada.models import BackgroundTask
from django.conf import settings
import os
from time import sleep,time
import traceback

def run():
    label   = 'pyscada.modbus.daemon'
    pid     = str(os.getpid())
    # read the global settings
    if settings.PYSCADA_MODBUS.has_key('polling_interval'):
        dt_set = float(settings.PYSCADA_MODBUS['polling_interval'])
    else:
        dt_set = 5 # default value is 5 seconds
    
    # register the task in Backgroudtask list
    bt = BackgroundTask(start=time(),label=label,message='daemonized',timestamp=time(),pid = pid)
    bt.save()
    bt_id = bt.pk
    # start the dataaquasition
    try:
        daq = client.DataAcquisition()
    except:
        var = traceback.format_exc()
        log.error("exeption in dataaquisition daemon, %s" % var)
        # on error mark the task as failed
        bt = BackgroundTask.objects.get(pk=bt_id)
        bt.message = 'failed'
        bt.failed = True
        bt.timestamp = time()
        bt.save()
        raise
    
    # mark the task as running
    bt = BackgroundTask.objects.get(pk=bt_id)
    bt.timestamp = time()
    bt.message = 'running...'
    bt.save()
    
    log.notice("started modbus dataaquisition daemon")
    err_count = 1
    # main loop
    while not bt.stop_daemon:
        t_start = time()
        try:
            daq.run()
            err_count = 1
        except:
            var = traceback.format_exc()
            # write log only 
            if err_count <= 3 or err_count == 10 or err_count%100 == 0:
                log.debug("occ: %d, exeption in dataaquisition daemon\n\n %s" % (err_count,var),-1)
            err_count +=1
            daq = client.DataAcquisition()
        bt = BackgroundTask.objects.get(pk=bt_id)   
        bt.timestamp = time()
        if dt_set>0:
            bt.load= 1.-max(min((time()-t_start)/dt_set,1),0)
        else:
            bt.load= 1
        bt.save()
        dt = dt_set -(time()-t_start)
        if dt>0:
            sleep(dt)
    
    ## will be called after stop signal
    log.notice("stopped dataaquisition daemon execution")
    bt = BackgroundTask.objects.get(pk=bt_id)    
    bt.timestamp = time()
    bt.done = True
    bt.message = 'stopped'
    bt.pid = 0
    bt.save()

    
