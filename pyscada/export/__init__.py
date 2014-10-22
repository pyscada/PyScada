# -*- coding: utf-8 -*-

from datetime import timedelta
from datetime import datetime
import os
from time import time, localtime, strftime,mktime
from numpy import float64,float32,int32,uint16,int16,uint8, nan
import math

from pyscada import log
from pyscada.models import Variable
from pyscada.models import RecordedDataFloat
from pyscada.models import RecordedDataInt
from pyscada.models import RecordedDataBoolean
from pyscada.models import RecordedTime
from pyscada.models import BackgroundTask
from pyscada.export.hdf5 import mat
from django.db import connection


"""
export measurements from the database to a file
"""


def timestamp_unix_to_matlab(timestamp):
    return (timestamp/86400)+719529


def export_database_to_h5(time_id_min=None,filename=None,time_id_max=None):
    tp = BackgroundTask(start=time(),label='data export',message='init',timestamp=time())
    tp.save()
    
    if filename is None:
        backup_file_path = os.path.expanduser('~/measurement_data_dumps')
        backup_file_name = 'measurement_data'
        if not os.path.exists(backup_file_path ):
            os.mkdir(backup_file_path)
        cdstr = strftime("%Y_%m_%d_%H%M",localtime())
        filename = os.path.join(backup_file_path,backup_file_name + '_' + cdstr + '.h5')
    
    bf = mat(filename)
    
    last_time_id = RecordedTime.objects.last().pk
    first_time_id = RecordedTime.objects.first().pk
    if type(time_id_min) is str:
        timestamp = mktime(datetime.strptime(time_id_min, "%d-%b-%Y %H:%M:%S").timetuple())
        time_id_min = RecordedTime.objects.filter(timestamp__gte=timestamp).first().pk
    if time_id_max is not None:
        last_time_id = min(last_time_id,time_id_max)
    
    if time_id_min is None:
        first_time_id = RecordedTime.objects.filter(timestamp__lte=time()-86460).last()
        if first_time_id:
            first_time_id = first_time_id.pk
        else:
            first_time_id = RecordedTime.objects.first().pk
    else:
        first_time_id = max(first_time_id,time_id_min)
    
    
    chunk_size = 17280
    first_time_id_chunk = first_time_id
    last_time_id_chunk = first_time_id + chunk_size
    if last_time_id_chunk > last_time_id:
        last_time_id_chunk = last_time_id
    
    tp.timestamp = time()
    tp.message = 'first chunk'
    tp.max = math.ceil((last_time_id-first_time_id)/chunk_size)
    tp.save()
    pre_data = {}
    while last_time_id>=last_time_id_chunk:
        pre_data = _export_data_to_h5(first_time_id_chunk,min(last_time_id_chunk,last_time_id),bf,tp,pre_data)
        first_time_id_chunk = last_time_id_chunk +1
        last_time_id_chunk += chunk_size
        tp.timestamp = time()
        tp.message = 'next chunk'
        tp.progress = tp.progress +1
        tp.save()
    
    tp.timestamp = time()
    tp.message = 'done'
    tp.progress = tp.max
    tp.done = 1
    tp.save()
    
def _export_data_to_h5(first_time_id,last_time_id,bf,tp,pre_data):
    tp.timestamp = time()
    tp.message = 'reading time values from SQL'
    tp.save()
    
    
    first_time = RecordedTime.objects.get(id=first_time_id)
    time_id_min = BackgroundTask.objects.filter(label='data acquision daemon',start__lte=first_time.timestamp).last()
    if time_id_min:
        time_id_min = RecordedTime.objects.filter(timestamp__lte = time_id_min.start).last()
        if time_id_min:
            time_id_min = time_id_min.id
            log.debug(("time_id_min %d to first_time_id %d")%(time_id_min,first_time_id))
        else:
            time_id_min = 1
    else:
        time_id_min = 1
        
    timevalues = [timestamp_unix_to_matlab(element) for element in RecordedTime.objects.filter(id__range = (first_time_id,last_time_id)).values_list('timestamp',flat=True)]
    time_ids = list(RecordedTime.objects.filter(id__range = (first_time_id,last_time_id)).values_list('id',flat=True))
    
    tp.timestamp = time()
    tp.message = 'writing time values to file'
    tp.save()
    
    
    bf.write_data('time',float64(timevalues))
    bf.reopen()
    
    data = {}
    active_vars = list(Variable.objects.filter(active = 1,record = 1,client__active=1).values_list('pk',flat=True));
    tp.timestamp = time()
    tp.message = 'reading float data values from SQL'
    tp.save()
    
    raw_data = list(RecordedDataFloat.objects.filter(time_id__range = (first_time_id,last_time_id),variable_id__in=active_vars).values_list('variable_id','time_id','value'))
    
    tp.timestamp = time()
    tp.message = 'prepare raw float data'
    tp.save()
    
    
    for item in raw_data:
        if not data.has_key(item[0]):
            data[item[0]] = []
        data[item[0]].append([item[1],item[2]])
    
    
    tp.timestamp = time()
    tp.message = 'reading int data values from SQL'
    tp.save()
    
    raw_data = []
    raw_data = list(RecordedDataInt.objects.filter(time_id__range = (first_time_id,last_time_id),variable_id__in=active_vars).values_list('variable_id','time_id','value'))
    
    tp.timestamp = time()
    tp.message = 'prepare raw int data'
    tp.save()
    
    
    for item in raw_data:
        if not data.has_key(item[0]):
            data[item[0]] = []
        data[item[0]].append([item[1],item[2]])
    
    tp.timestamp = time()
    tp.message = 'reading bool data values from SQL'
    tp.save()
    
    raw_data = []
    raw_data = list(RecordedDataBoolean.objects.filter(time_id__range = (first_time_id,last_time_id),variable_id__in=active_vars).values_list('variable_id','time_id','value'))
    
    tp.timestamp = time()
    tp.message = 'prepare raw bool data'
    tp.save()
    
    
    for item in raw_data:
        if not data.has_key(item[0]):
            data[item[0]] = []
        data[item[0]].append([item[1],item[2]])
    
    raw_data = []
    
    tp.timestamp = time()
    tp.message = 'writing data to file'
    tp.save()
    
    pre_data = {}
    for var in Variable.objects.filter(active = 1,record = 1,client__active=1).order_by('pk'):
        tp.timestamp = time()
        tp.message = 'processing variable_id %d'%var.pk
        tp.save()
        
        var_id = var.pk
        variable_class = var.value_class
        first_record = False
        if data.has_key(var_id):
            records = data[var_id]
            if records[0][0] == first_time_id:
                first_record = True
            
        else:
            records = []
            
        if not first_record:
            if pre_data.has_key(var_id):
                records.insert(0,pre_data[var_id])
                first_record = True
            else:
                first_record = _last_matching_record(variable_class,first_time_id,var_id,time_id_min)
                if first_record:
                    records.insert(0,first_record)
        
        if not first_record and not records:
            tmp = [0]*len(time_ids)
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
            
            bf.write_data(var.name,tmp)
            bf.reopen()
            continue
        
        #blow up data ##########################################################
        
        tmp = [0]*len(time_ids)
        t_idx = 0
        v_idx = 0
        nb_v_idx = len(records)-1
        for id in time_ids:
            if nb_v_idx < v_idx: 
                if t_idx > 0:
                    tmp[t_idx] = tmp[t_idx-1]
            else:
                if records[v_idx][0]==id:
                    tmp[t_idx] = records[v_idx][1]
                    laid = id
                    v_idx += 1
                elif t_idx > 0:
                    tmp[t_idx] = tmp[t_idx-1]
                elif records[v_idx][0]<=id:
                    tmp[t_idx] = records[v_idx][1]
                    laid = id
                    v_idx += 1
    
                if nb_v_idx > v_idx:
                    logged = False
                    while records[v_idx][0]<=id and v_idx <= nb_v_idx:
                        if not logged:
                            log.debug(("double id %d in var %d")%(id,var_id))
                            logged = True
                        v_idx += 1
            t_idx += 1
        pre_data[var_id] = tmp[-1]        
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
        
        bf.write_data(var.name,tmp)
        bf.reopen()
    return pre_data
        
    
    """
    end for ###################################################################################
    """
    

def _last_matching_record(variable_class,time_id,variable_id,time_id_min):
    cursor = connection.cursor()
    if variable_class.upper() in ['FLOAT32','SINGLE','FLOAT','FLOAT64','REAL']:
        item = cursor.execute("SELECT time_id,value FROM pyscada_recordeddatafloat WHERE time_id <= %s AND time_id >= %s AND  variable_id = %s ORDER BY time_id DESC LIMIT 1;",[time_id,time_id_min,variable_id])
        #item = cursor.execute("SELECT time_id,value FROM pyscada_recordeddatafloat WHERE id = (SELECT max(id) FROM pyscada_recordeddataboolean WHERE time_id <= %s AND time_id >= %s AND  variable_id = %s);",[time_id,time_id_min,variable_id])
    elif variable_class.upper() in ['INT32','UINT32','INT16','INT','WORD','UINT','UINT16']:
        item = cursor.execute("SELECT time_id,value FROM pyscada_recordeddataint WHERE time_id <= %s AND time_id >= %s AND variable_id = %s ORDER BY time_id DESC LIMIT 1;",[time_id,time_id_min,variable_id])
        #item = cursor.execute("SELECT time_id,value FROM pyscada_recordeddataint WHERE id = (SELECT max(id) FROM pyscada_recordeddataboolean WHERE time_id <= %s AND time_id >= %s AND  variable_id = %s);",[time_id,time_id_min,variable_id])

    elif variable_class.upper() in ['BOOL']:
        item = cursor.execute("SELECT time_id,value FROM pyscada_recordeddataboolean WHERE time_id <= %s AND time_id >= %s AND variable_id = %s ORDER BY time_id DESC LIMIT 1;",[time_id,time_id_min,variable_id])    
        #item = cursor.execute("SELECT time_id,value FROM pyscada_recordeddataboolean WHERE id = (SELECT max(id) FROM pyscada_recordeddataboolean WHERE time_id <= %s AND time_id >= %s AND  variable_id = %s);",[time_id,time_id_min,variable_id])

    else:
        return None
    
    if 1 == item:
        return cursor.fetchone()
    else:
        return None
'''
def _last_matching_records(variable_class,time_id_min,time_id_max,variable_id):
    cursor = connection.cursor()
    if variable_class.upper() in ['FLOAT32','SINGLE','FLOAT','FLOAT64','REAL'] :
        item = cursor.execute("SELECT time_id,value FROM pyscada_recordeddatafloat WHERE time_id > %s AND time_id < %s AND variable_id = %s;",[time_id_min,time_id_max,variable_id])
    elif variable_class.upper() in ['INT32','UINT32','INT16','INT','WORD','UINT','UINT16'] :
        item = cursor.execute("SELECT time_id,value FROM pyscada_recordeddataint WHERE time_id > %s AND time_id < %s AND variable_id = %s;",[time_id_min,time_id_max,variable_id])
    elif variable_class.upper() in ['BOOL'] :
        item = cursor.execute("SELECT time_id,value FROM pyscada_recordeddataboolean WHERE time_id > %s AND time_id < %s AND variable_id = %s;",[time_id_min,time_id_max,variable_id])

    else:
        return None
    
    if item > 0:
        return cursor.fetchall()
    else:
        return None
'''