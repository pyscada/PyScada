# -*- coding: utf-8 -*-

from pyscada import log
from pyscada.models import Variable
from pyscada.models import RecordedDataCache
from pyscada.models import BackgroundTask
from pyscada.models import BackupFile
from pyscada.export.hdf5 import mat

from django.conf import settings
import os
from time import time, localtime, strftime,mktime,sleep
from numpy import float64,float32,int32,uint16,int16,uint8,nan,inf
import math

"""
export measurements from the database to a file
"""


def timestamp_unix_to_matlab(timestamp):
    return (timestamp/86400)+719529

def drange(start, stop, step):
    r = start
    while r < stop:
        yield r
        r += step

def backup_cache_data():
    # check for active backuptasks
    if BackgroundTask.objects.filter(pid__gt = 0, label= 'pyscada.export.backup_cache_data'):
        wait_count = 0
        tp = BackgroundTask(start=time(),label='pyscada.export.backup_cache_data',message='waiting...',timestamp=time(),pid=os.getpid())
        tp.save()
        tp_id = tp.pk
        while BackgroundTask.objects.filter(pid__gt = 0, label= 'pyscada.export.backup_cache_data',pk__lt=tp_id):
            for bt in BackgroundTask.objects.filter(pid__gt = 0, label= 'pyscada.export.backup_cache_data',pk__lt=tp_id):
                # check if process is alive
                try:
                    os.kill(bt.pid, 0)
                except OSError:
                    # process is dead
                    bt.pid = 0
                    bt.message = 'dead'
                    bt.timestamp = time()
                    bt.save()
                    
            if wait_count > 3600:
                log.notice("data export daemon: instance already running")
                tp = BackgroundTask.objects.get(pk=tp_id)
                tp.done = True
                tp.progress = 1
                tp.max = 1
                tp.pid = 0
                tp.message   = 'finished'
                tp.timestamp = time()
                tp.save()
                return
            wait_count += 1
            if wait_count%15 == 0:
                tp = BackgroundTask.objects.get(pk=tp_id)
                tp.timestamp = time()
                tp.message('waiting...')
                tp.save()
            sleep(1)
        
        tp = BackgroundTask.objects.get(pk=tp_id)
        tp.timestamp = time()
        tp.message = 'init'
        tp.save()
    else:    
        tp = BackgroundTask(start=time(),label='pyscada.export.backup_cache_data',message='init',timestamp=time(),pid=os.getpid())
        tp.save()
        tp_id = tp.pk
    # set file path
    if settings.PYSCADA_EXPORT.has_key('backup_path'):
        backup_file_path = os.path.expanduser(settings.PYSCADA_EXPORT['backup_path'])
    else:
        backup_file_path = os.path.expanduser('~/measurement_data_dumps')
    # set filename
    if settings.PYSCADA_EXPORT.has_key('backup_filename_prefix'):    
        backup_file_name = settings.PYSCADA_EXPORT['backup_filename_prefix']
    else:
        backup_file_name = 'measurement_data'
    # create dir if nessecery
    if not os.path.exists(backup_file_path ):
        os.mkdir(backup_file_path)
        
    
    
    if  BackupFile.objects.filter(active=False).last():
        first_time = BackupFile.objects.last().time_end
    else:
        first_time = 0
    
    
    tp = BackgroundTask.objects.get(pk=tp_id)
    tp.timestamp = time()
    tp.message = 'reading cache data'
    tp.save()
    
    active_vars = Variable.objects.filter(active = 1,record = 1,client__active=1).order_by('pk')
    raw_data = list(RecordedDataCache.objects.filter(last_update__gt=first_time,variable_id__in=active_vars).values_list('variable_id','float_value','int_value','last_update','last_change'))
    data = {}
    
    
    tp = BackgroundTask.objects.get(pk=tp_id)
    tp.timestamp = time()
    tp.message = 'prepare raw data'
    tp.save()
    
    last_time = first_time
    if first_time == 0:
        first_time = inf
        
    for var in raw_data:
        last_time   = max(last_time,var[3])
        first_time  = min(first_time,var[3])
        if not data.has_key(var[0],):
            data[var[0]] = [];
        if var[4] != var[3]:  # if value is constant add a pantom datapoint
            if var[1]!=None:
                data[var[0]].append([timestamp_unix_to_matlab(var[4]),var[1]])
            else:
                data[var[0]].append([timestamp_unix_to_matlab(var[4]),var[2]])
        if var[1]!=None:
            data[var[0]].append([timestamp_unix_to_matlab(var[3]),var[1]])
        else:
            data[var[0]].append([timestamp_unix_to_matlab(var[3]),var[2]])
    
    ## time vector
    if settings.PYSCADA_EXPORT.has_key('recording_interval'):
        rec_interv = settings.PYSCADA_EXPORT['recording_interval']
    else:
        rec_interv = 5 # seconds
    
    timevalues = list(drange(timestamp_unix_to_matlab(first_time+rec_interv),timestamp_unix_to_matlab(last_time),rec_interv/24.0/60.0/60.0))
    
    tp = BackgroundTask.objects.get(pk=tp_id)
    tp.timestamp = time()
    tp.message = 'writing time values to file'
    tp.save()
    if not raw_data:
        log.notice("data export daemon: no data to export")
        tp = BackgroundTask.objects.get(pk=tp_id)
        tp.done = True
        tp.progress = 1
        tp.max = 1
        tp.pid = 0
        tp.message   = 'finished'
        tp.timestamp = time()
        tp.save()
        return
        
    filename = os.path.join(backup_file_path,backup_file_name + '_%s.h5'%strftime("%Y_%m_%d_%H%M",localtime()))
    bf = BackupFile(file=filename)
    bf.active = True
    bf.time_begin = first_time
    bf.time_end   = last_time
    bf.save()
    bf_id = bf.pk  
    
    # write time values to hdf5 file
    h5 = mat(filename)
    h5.write_data('time',float64(timevalues))
    h5.reopen()
    
    
    ## write variables to file
    for var in Variable.objects.filter(active = 1,record = 1,client__active=1).order_by('pk'):
            # init empty temporary value
            tmp = [0.0]*len(timevalues)
            if data.has_key(var.id):
                tp = BackgroundTask.objects.get(pk=tp_id)
                tp.timestamp = time()
                tp.message = 'write variable %d'% var.id
                tp.progress = tp.progress + 1
                tp.save()
                # prepare values
                c = 0 # data idx counter
                t = 0 # time idx counter
                for timevalue in drange(timestamp_unix_to_matlab(first_time+rec_interv),timestamp_unix_to_matlab(last_time),rec_interv/24.0/60.0/60.0):
                    m = 0.0 # mean counter
                    mean_tmp = 0.0 # mean sum value
                    if c >= len(data[var.id]):
                        continue
                    while data[var.id][c][0] <= timevalue:
                        mean_tmp += data[var.id][c][1]     
                        c += 1
                        m += 1.0
                        if c >= len(data[var.id]):
                            break
                        
                    if m>0:    
                        tmp[t] = mean_tmp/m
                    else:
                        if t >0:
                            tmp[t] = tmp[t-1]
                        else:
                            tmp[t] = 0
                    t += 1
                            
            variable_class = var.value_class
            if variable_class.upper() in ['FLOAT','FLOAT64','DOUBLE'] :
                tmp = float64(tmp)
            elif variable_class.upper() in ['FLOAT32','SINGLE','REAL'] :
                tmp = float32(tmp)
            elif  variable_class.upper() in ['INT32']:
                tmp = int32(tmp)
            elif  variable_class.upper() in ['WORD','UINT','UINT16']:
                tmp = uint16(tmp)    
            elif  variable_class.upper() in ['INT16','INT']:
                tmp = int16(tmp)
            elif variable_class.upper() in ['BOOL']:
                tmp = uint8(tmp)
            else:
                tmp = float64(tmp)
            
            h5.write_data(var.name,tmp)
            h5.reopen()
    
    # update Backupfile info
    bf = BackupFile.objects.get(pk = bf_id)
    bf.active = False
    bf.save()
    # update task info
    tp = BackgroundTask.objects.get(pk=tp_id)
    tp.done = True
    tp.progress = 1
    tp.max = 1
    tp.message   = 'finished'
    tp.timestamp = time()
    tp.pid = 0
    tp.save()