#!/usr/bin/python
# -*- coding: utf-8 -*- 
from pyscada import log
from pyscada.export import backup_cache_data
from pyscada.models import BackgroundTask
from django.conf import settings
import os
from time import sleep,time
import traceback

def run():
    label   = 'pyscada.export.daemon'
    pid     = str(os.getpid())
    # read the global settings
    if settings.PYSCADA_EXPORT.has_key('write_to_file_interval'):
        dt_set = float(settings.PYSCADA_EXPORT['write_to_file_interval'])
    else:
        dt_set = 6*60 # default value is 6 hours
    dt_set = dt_set*60; # minutes to seconds conversion
    # register the task in Backgroudtask list
    bt = BackgroundTask(start=time(),label=label,message='daemonized',timestamp=time(),pid = pid)
    bt.save()
    
    # init the data backup export
#     try:
#         backup_cache_data()
#     except:
#         var = traceback.format_exc()
#         log.error("exeption in data export daemon, %s" % var)
#         # on error mark the task as failed
#         bt = BackgroundTask.objects.filter(pid=pid).last()
#         bt.message = 'failed'
#         bt.failed = True
#         bt.timestamp = time()
#         bt.save()
#         raise
    
    # mark the task as running
    bt = BackgroundTask.objects.filter(pid=pid).last()
    bt.timestamp = time()
    bt.message = 'running...'
    bt.save()
    
    log.notice("started data export daemon")
    err_count = 1
    
    ## main loop
    t_start = time() - dt_set
    load    = 0
    while not bt.stop_daemon:
        t_loop_start = time()
        
        # start action
        if (time()-t_start) >= dt_set:
            t_start = time()
            try:
                backup_cache_data()
                err_count = 1
            except:
                var = traceback.format_exc()
                # write log only 
                if err_count <= 3 or err_count == 10 or err_count%100 == 0:
                    log.debug("occ: %d, exeption in data export daemon\n\n %s" % (err_count,var),-1)
                err_count +=1
            if dt_set>0:
                load= 1.-max(min((time()-t_start)/dt_set,1),0)
            else:
                load= 1
            
        

        # update taskinfo
        bt = BackgroundTask.objects.filter(pid=pid).last()   
        bt.timestamp = time()
        bt.load= load
        bt.save()
        dt = 1 -(time()-t_loop_start) # restart loop every second
        if dt>0:
            sleep(dt)
    
    ## will be called after stop signal
    log.notice("stopped data export daemon execution")
    bt = BackgroundTask.objects.filter(pid=pid).last()    
    bt.timestamp = time()
    bt.done = True
    bt.message = 'stopped'
    bt.pid = 0
    bt.save()

        
