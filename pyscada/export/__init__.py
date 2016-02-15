# -*- coding: utf-8 -*-
import pyscada

__version__ = pyscada.__version__
__author__  = pyscada.__author__

default_app_config = 'pyscada.export.apps.PyScadaExportConfig'

# PyScada
from pyscada import log
from pyscada.utils import validate_value_class, export_xml_config_file
from pyscada.models import Variable, Device, Unit, RecordedDataFloat, RecordedDataInt, RecordedDataBoolean, RecordedTime, BackgroundTask 
from pyscada.export.hdf5 import mat_compatible_h5
from pyscada.export.hdf5 import unix_time_stamp_to_matlab_datenum
from pyscada.export.csv import excel_compatible_csv
from pyscada.export.csv import unix_time_stamp_to_excel_datenum
# Django
from django.db import connection
from django.core import serializers
from django.conf import settings

# other
from datetime import timedelta
from datetime import datetime
import os
from time import time, localtime, strftime,mktime
from numpy import float64,float32,int32,uint32,uint16,int16,uint8, nan
import math



def export_measurement_data_to_file(time_id_min=None,filename=None,time_id_max=None,active_vars=None,file_extension=None,**kwargs):
    """
    export measurements from the database to a file
    """
    if kwargs.has_key('task_identifier'):
        if BackgroundTask.objects.filter(identifier = kwargs['task_identifier'],failed=0):
            return
        else:
            tp = BackgroundTask(start=time(),label='pyscada.export.export_measurement_data_%s'%kwargs['task_identifier'],message='init',timestamp=time(),pid=str(os.getpid()),identifier = kwargs['task_identifier'])
    else:
        tp = BackgroundTask(start=time(),label='pyscada.export.export_measurement_data_to_file',message='init',timestamp=time(),pid=str(os.getpid()))
    
    tp.save()
    
    if filename is None:
        if file_extension is None:
            file_extension = '.h5'
        if hasattr(settings,'PYSCADA_EXPORT'):
            if settings.PYSCADA_EXPORT.has_key('output_folder'):
                backup_file_path = os.path.expanduser(settings.PYSCADA_EXPORT['output_folder'])
            else:
                backup_file_path = os.path.expanduser('~/measurement_data_dumps')
        else:
            backup_file_path = os.path.expanduser('~/measurement_data_dumps')
        
        backup_file_name = 'measurement_data'
        if hasattr(settings,'PYSCADA_EXPORT'):
            if settings.PYSCADA_EXPORT.has_key('file_prefix'):
                backup_file_name = settings.PYSCADA_EXPORT['file_prefix'] + backup_file_name
            
        if not os.path.exists(backup_file_path ):
            os.mkdir(backup_file_path)
        cdstr = strftime("%Y_%m_%d_%H%M",localtime())
        if kwargs.has_key('filename_suffix'):
            filename = os.path.join(backup_file_path,backup_file_name + '_' + cdstr + '_' + kwargs['filename_suffix'] + file_extension)
            xml_filename = os.path.join(backup_file_path,backup_file_name + '_' + cdstr + '_' + kwargs['filename_suffix'] + '.xml')
        else:
            filename = os.path.join(backup_file_path,backup_file_name + '_' + cdstr + file_extension)
            xml_filename = os.path.join(backup_file_path,backup_file_name + '_' + cdstr + '.xml')
    else:
        xml_filename    = filename.split('.')[0] + '.xml'
        file_extension  = '.' + filename.split('.')[-1]
    
    if not file_extension in ['.h5','.mat','.csv']:
        tp.timestamp = time()
        tp.message = 'failed wrong file type'
        tp.failed = 1
        tp.save()
        return
    # 
    if active_vars is None:
        active_vars = list(Variable.objects.filter(active = 1,record = 1,device__active=1).values_list('pk',flat=True))
    else:
        if type(active_vars) is str:
            if active_vars == 'all':
                active_vars = list(Variable.objects.all().values_list('pk',flat=True))
            else:
                active_vars = list(Variable.objects.filter(active = 1,record = 1,device__active=1).values_list('pk',flat=True))
        else:
            active_vars = list(Variable.objects.filter(pk__in = active_vars, active = 1,record = 1,device__active=1).values_list('pk',flat=True))

            
    def _export_data_to_file():
        tp.timestamp = time()
        tp.message = 'reading time values from SQL'
        tp.save()


        if file_extension in ['.h5','.mat']:
            timevalues = [unix_time_stamp_to_matlab_datenum(element) for element in RecordedTime.objects.filter(id__range = (first_time_id_chunk,last_time_id_chunk)).values_list('timestamp',flat=True)]
        elif file_extension in ['.csv']:
            timevalues = [unix_time_stamp_to_excel_datenum(element) for element in RecordedTime.objects.filter(id__range = (first_time_id_chunk,last_time_id_chunk)).values_list('timestamp',flat=True)]
        time_ids = list(RecordedTime.objects.filter(id__range = (first_time_id_chunk,last_time_id_chunk)).values_list('id',flat=True))

        tp.timestamp = time()
        tp.message = 'writing time values to file'
        tp.save()


        bf.write_data('time',float64(timevalues),\
            id = 0,\
            description="global time vector",\
            value_class = validate_value_class('FLOAT64'),\
            unit = "Days since 0000-1-1 00:00:00")

        data = {}
        
        tp.timestamp = time()
        tp.message = 'reading float data values from SQL'
        tp.save()

        raw_data = list(RecordedDataFloat.objects.filter(time_id__range = (first_time_id_chunk,last_time_id_chunk),variable_id__in=active_vars).values_list('variable_id','time_id','value'))

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
        raw_data = list(RecordedDataInt.objects.filter(time_id__range = (first_time_id_chunk,last_time_id_chunk),variable_id__in=active_vars).values_list('variable_id','time_id','value'))

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
        raw_data = list(RecordedDataBoolean.objects.filter(time_id__range = (first_time_id_chunk,last_time_id_chunk),variable_id__in=active_vars).values_list('variable_id','time_id','value'))

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

        
        for var in Variable.objects.filter(pk__in=active_vars).order_by('pk'):
            tp.timestamp = time()
            tp.message = 'processing variable_id %d'%var.pk
            tp.save()

            var_id = var.pk
            variable_class = var.value_class
            first_record = False
            if data.has_key(var_id):
                records = data[var_id]
                if records[0][0] == first_time_id_chunk:
                    first_record = True

            else:
                records = []

            if not first_record: # get the most recent value
                if pre_data.has_key(var_id): # if there is a prev value stored 
                    records.insert(0,[first_time_id_chunk,pre_data[var_id]])
                    first_record = True
                else: # try to get it from the database only on the first run
                    first_record = _last_matching_record(variable_class,first_time_id_chunk,var_id,time_id_min) 
                    if first_record:
                        records.insert(0,first_record)

            if not first_record and not records:
                # write zeros if no data is avail
                if hasattr(var.unit,'udunit'):
                    udunit = var.unit.udunit
                else :
                    udunit = 'None'
                bf.write_data(var.name,_cast_value([0]*len(time_ids),variable_class),\
                id = var_id,\
                description=var.description,\
                value_class = validate_value_class(var.value_class),\
                unit = udunit)
                pre_data[var_id] = 0 # add 0 to prev value list to speed up next run
                continue

            ## blow up data ########################################################
            tmp = [0]*len(time_ids)
            t_idx = 0                 # index of the time value record
            v_idx = 0                 # index of the value in record
            nb_v_idx = len(records)-1 # number of values in record array
            for id in time_ids:       # 
                if nb_v_idx < v_idx:  # no records left, 
                    if t_idx > 0:
                        tmp[t_idx] = tmp[t_idx-1]
                else:                 # 
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
                        # if more then 1 record has the same time id drop the 
                        # duplicate values
                        while records[v_idx][0]<=id and v_idx <= nb_v_idx:
                            if not logged:
                                log.debug(("double id %d in var %d")%(id,var_id))
                                logged = True
                            if nb_v_idx > v_idx: # CHANGED
                                v_idx += 1
                            else:
                                break
                t_idx += 1
            pre_data[var_id] = tmp[-1]
            ## write data to file ##################################################
            if hasattr(var.unit,'udunit'):
                udunit = var.unit.udunit
            else :
                udunit = 'None'
            bf.write_data(var.name,_cast_value(tmp,variable_class),\
            id = var_id,\
            description=var.description,\
            value_class = validate_value_class(var.value_class),\
            unit =  udunit)
        ## end for #################################################################
    if hasattr(settings,'PYSCADA_META'):
        if settings.PYSCADA_META.has_key('description'):
            description = settings.PYSCADA_META['description']
        else:
            description = 'None'
        if settings.PYSCADA_META.has_key('name'):
            name = settings.PYSCADA_META['name']
        else:
            name = 'None'
    else:
        description = 'None'
        name = 'None'
    if file_extension in ['.h5','.mat']:
        bf = mat_compatible_h5(filename,version = '1.1',description = description ,name = name, creation_date = strftime('%d-%b-%Y %H:%M:%S'))
    elif file_extension in ['.csv']:
        bf = excel_compatible_csv(filename,version = '1.1',description = description ,name = name, creation_date = strftime('%d-%b-%Y %H:%M:%S'))
    # export config to an separate file to avoid attr > 64k
    export_xml_config_file(xml_filename)
    
    last_time_id = RecordedTime.objects.last().pk
    first_time_id = RecordedTime.objects.first().pk
    if type(time_id_min) is str:
        timestamp = mktime(datetime.strptime(time_id_min, "%d-%b-%Y %H:%M:%S").timetuple())
        if timestamp:
            time_id_min = RecordedTime.objects.filter(timestamp__gte=timestamp).first().pk
        else:
            time_id_min = first_time_id
            
    if type(time_id_max) is str:
        timestamp = mktime(datetime.strptime(time_id_max, "%d-%b-%Y %H:%M:%S").timetuple())
        if timestamp:
            time_id_max = RecordedTime.objects.filter(timestamp__lte=timestamp).last().pk
        else:
            time_id_max = last_time_id
        
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

    if connection.vendor == 'sqlite':
        # on sqlite limit querys to less then 999 elements
        chunk_size = 998
    else:
        chunk_size = 17200
        
    first_time_id_chunk = first_time_id
    last_time_id_chunk = first_time_id + chunk_size - 1
    if last_time_id_chunk > last_time_id:
        last_time_id_chunk = last_time_id

    tp.timestamp = time()
    tp.message = 'first chunk'
    tp.max = math.ceil((last_time_id-first_time_id)/chunk_size)
    tp.save()
    pre_data = {}
    
    first_time = RecordedTime.objects.get(id=first_time_id_chunk)
    time_id_min = BackgroundTask.objects.filter(label='pyscada.modbus.daemon',start__lte=first_time.timestamp).last() # FIXME 
    if not time_id_min:
        time_id_min = BackgroundTask.objects.filter(label='data acquision daemon',start__lte=first_time.timestamp).last()
    if time_id_min:
        time_id_min = RecordedTime.objects.filter(timestamp__lte = time_id_min.start).last()
        if time_id_min:
            time_id_min = time_id_min.id
            log.debug(("time_id_min %d to first_time_id %d")%(time_id_min,first_time_id_chunk))
        else:
            time_id_min = 1
    else:
        time_id_min = 1

    while first_time_id_chunk < last_time_id:
        # export data
        _export_data_to_file()
        bf.reopen()# moved here to avoid frequent write to hdf5 file
        # next chunk
        first_time_id_chunk = last_time_id_chunk + 1
        last_time_id_chunk  = first_time_id_chunk + chunk_size - 1
        last_time_id_chunk  = min(last_time_id_chunk,last_time_id)
        # update task progress
        tp.timestamp = time()
        tp.message = 'next chunk'
        tp.progress = tp.progress +1
        tp.save()
    
    bf.close_file()
    tp.timestamp = time()
    tp.message = 'done'
    tp.progress = tp.max
    tp.done = 1
    tp.save()
    
    



def _last_matching_record(variable_class,time_id,variable_id,time_id_min):
    cursor = connection.cursor()
    if variable_class.upper() in ['FLOAT32','SINGLE','FLOAT','FLOAT64','REAL']:
        item = cursor.execute("SELECT time_id,value FROM pyscada_recordeddatafloat WHERE time_id <= %s AND time_id >= %s AND  variable_id = %s ORDER BY time_id DESC LIMIT 1;",[time_id,time_id_min,variable_id])
        #item = cursor.execute("SELECT time_id,value FROM pyscada_recordeddatafloat WHERE id = (SELECT max(id) FROM pyscada_recordeddataboolean WHERE time_id <= %s AND time_id >= %s AND  variable_id = %s);",[time_id,time_id_min,variable_id])
    elif variable_class.upper() in ['INT32','UINT32','INT16','INT','WORD','UINT','UINT16']:
        item = cursor.execute("SELECT time_id,value FROM pyscada_recordeddataint WHERE time_id <= %s AND time_id >= %s AND variable_id = %s ORDER BY time_id DESC LIMIT 1;",[time_id,time_id_min,variable_id])
        #item = cursor.execute("SELECT time_id,value FROM pyscada_recordeddataint WHERE id = (SELECT max(id) FROM pyscada_recordeddataboolean WHERE time_id <= %s AND time_id >= %s AND  variable_id = %s);",[time_id,time_id_min,variable_id])

    elif variable_class.upper() in ['BOOL','BOOLEAN']:
        item = cursor.execute("SELECT time_id,value FROM pyscada_recordeddataboolean WHERE time_id <= %s AND time_id >= %s AND variable_id = %s ORDER BY time_id DESC LIMIT 1;",[time_id,time_id_min,variable_id])
        #item = cursor.execute("SELECT time_id,value FROM pyscada_recordeddataboolean WHERE id = (SELECT max(id) FROM pyscada_recordeddataboolean WHERE time_id <= %s AND time_id >= %s AND  variable_id = %s);",[time_id,time_id_min,variable_id])

    else:
        return None

    if 1 == item:
        return cursor.fetchone()
    else:
        return None

def export_data_tables(**kwargs):
    '''
    export a set of tables to h5 file
    '''


    last_time_id = RecordedTime.objects.last().pk
    if kwargs.has_key('last_time_id'):
        last_time_id = min(last_time_id,kwargs['last_time_id'])

    first_time_id = RecordedTime.objects.first().pk
    if kwargs.has_key('first_time_id'):
        first_time_id = max(first_time_id,kwargs['first_time_id'])

    if kwargs.has_key('last_time_str'):
        timestamp = mktime(datetime.strptime(kwargs['last_time_str'], "%d-%b-%Y %H:%M:%S").timetuple())
        time_id_max = RecordedTime.objects.filter(timestamp__gte=timestamp).first()
        if time_id_max is not None:
            last_time_id = min(last_time_id,time_id_max.pk)

    if kwargs.has_key('first_time_str'):
        timestamp = mktime(datetime.strptime(kwargs['first_time_str'], "%d-%b-%Y %H:%M:%S").timetuple())
        time_id_min = RecordedTime.objects.filter(timestamp__lte=timestamp).last()
        if time_id_min is not None:
            first_time_id = max(first_time_id,time_id_min.pk)

    if kwargs.has_key('table_list'):
        table_list = kwargs['table_list']
    else:
        table_list = ['RecordedDataFloat_h5','RecordedDataInt_h5','RecordedDataBoolean_h5','RecordedTime_h5','Variable_xml']
    tp = BackgroundTask(start=time(),label='export tables',message='init',timestamp=time(),pid=os.getpid())
    tp.progress = 0
    tp.save()
    bt_id = tp.pk
    cdstr = strftime("%Y_%m_%d_%H%M",localtime())
    backup_file_path = os.path.expanduser('~/measurement_data_dumps')
    if not os.path.exists(backup_file_path ):
        os.mkdir(backup_file_path)
    for table in table_list:
        backup_file_name = 'table_dump_' + table[:-3]
        filename = os.path.join(backup_file_path,backup_file_name + '_' + cdstr + '.h5')
        if table == 'RecordedDataFloat_h5':
            tp.message = 'exporting RecordedDataFloat_h5'
            tp.timestamp=time()
            tp.save()
            first_id = RecordedDataFloat.objects.filter(time_id__gte = first_time_id).first().pk
            last_id = RecordedDataFloat.objects.filter(time_id__lte = last_time_id).last().pk
            export_table_to_h5(table=table[:-3],first_id = first_id,last_id = last_id,filename = filename)
        elif table == 'RecordedDataInt_h5':
            tp.message = 'exporting RecordedDataInt_h5'
            tp.timestamp=time()
            tp.save()
            first_id = RecordedDataInt.objects.filter(time_id__gte = first_time_id).first().pk
            last_id = RecordedDataInt.objects.filter(time_id__lte = last_time_id).last().pk
            export_table_to_h5(table=table[:-3],first_id = first_id,last_id = last_id,filename = filename)
        elif table == 'RecordedDataBoolean_h5':
            tp.message = 'exporting RecordedDataBoolean_h5'
            tp.timestamp=time()
            tp.save()
            first_id = RecordedDataBoolean.objects.filter(time_id__gte = first_time_id).first().pk
            last_id = RecordedDataBoolean.objects.filter(time_id__lte = last_time_id).last().pk
            export_table_to_h5(table=table[:-3],first_id = first_id,last_id = last_id,filename = filename)
        elif table == 'RecordedTime_h5':
            tp.message = 'exporting RecordedTime_h5'
            tp.timestamp=time()
            tp.save()
            first_id = first_time_id
            last_id = last_time_id
            export_table_to_h5(table=table[:-3],first_id = first_id,last_id = last_id,filename = filename)
        elif table == 'Variable_xml':
            tp.message = 'exporting Variable_xml'
            tp.timestamp=time()
            tp.save()
            if kwargs.has_key('filename'):
                filename = kwargs['filename']
            else:
                backup_file_name = 'table_dump_' + table[:-4]
                filename = os.path.join(backup_file_path,backup_file_name + '_' + cdstr + '.xml')
            XMLSerializer = serializers.get_serializer("xml")
            xml_serializer = XMLSerializer()
            with open(filename, "w") as file_:
                xml_serializer.serialize(list(Variable.objects.all())+list(Unit.objects.all()) + list(Device.objects.all()), stream=file_)

        tp.message = 'done'
        tp.timestamp=time()
        tp.done = True
        tp.save()




def export_table_to_h5(**kwargs):
    '''
    export a full table to a h5 file
    '''

    # Table name
    if kwargs.has_key('table'):
        table = kwargs['table']
    else:
        table = None


    # range to export
    if kwargs.has_key('first_id'):
        first_id = kwargs['first_id']
    else:
        first_id = 1

    if kwargs.has_key('last_id'):
        last_id = kwargs['last_id']
    else:
        if table == 'RecordedDataFloat':
            last_id = RecordedDataFloat.objects.all().last().pk
        elif table == 'RecordedDataInt':
            last_id = RecordedDataInt.objects.all().last().pk
        elif table == 'RecordedDataBoolean':
            last_id = RecordedDataBoolean.objects.all().last().pk
        elif table == 'RecordedTime':
            last_id = RecordedTime.objects.all().last().pk
        else:
            return


    if kwargs.has_key('filename'):
        filename = kwargs['filename']
    else:
        backup_file_path = os.path.expanduser('~/measurement_data_dumps')
        backup_file_name = 'table_dump_' + table
        if not os.path.exists(backup_file_path ):
            os.mkdir(backup_file_path)
        cdstr = strftime("%Y_%m_%d_%H%M",localtime())
        filename = os.path.join(backup_file_path,backup_file_name + '_' + cdstr + '.h5')

    if kwargs.has_key('chunk_size'):
        chunk_size = kwargs['chunk_size']
    else:
        chunk_size = math.pow(10,6)



    tp = BackgroundTask(start=time(),label='export.export_table_to_h5',message='init',timestamp=time(),max=math.ceil((last_id-first_id)/chunk_size),pid=os.getpid())
    tp.progress = 0
    tp.save()
    bt_id = tp.pk
    if tp.max > 1:
        # set to background task
        os.nice(20)
    def check_and_update_task_info(message):
        tp = BackgroundTask.objects.get(pk=bt_id)
        if tp.stop_daemon:
            return False
        tp.timestamp = time()
        tp.message = message
        tp.save()
        return True

    def _export_table_recorded_time():
        if not check_and_update_task_info('reading time data (id: %d - %d of %d)'%(first_id_chunk,last_id_chunk,last_id)):
            return

        data = list(RecordedTime.objects.filter(\
        id__range=(first_id_chunk,last_id_chunk)).values_list('id','timestamp'))
        if not check_and_update_task_info('writing time data row id (id: %d - %d of %d)'%(first_id_chunk,last_id_chunk,last_id)):
            return
        ids = [data[i][0] for i in range(0,len(data)-1)]
        bf.write_data('id',uint32(ids))
        bf.reopen()
        ids = []
        if not check_and_update_task_info('writing time data row timestamp (id: %d - %d of %d)'%(first_id_chunk,last_id_chunk,last_id)):
            return
        values = [data[i][1] for i in range(0,len(data)-1)]
        bf.write_data('value',float64(values))
        bf.reopen()
        values = []

    def _export_table_recorded_data_float():
        if not check_and_update_task_info('reading float data (id: %d - %d of %d)'%(first_id_chunk,last_id_chunk,last_id)):
            return
        data = list(RecordedDataFloat.objects.filter(\
        id__range=(first_id_chunk,last_id_chunk)).values_list('id','value','variable_id','time_id'))
        if not check_and_update_task_info('writing float data row id (id: %d - %d of %d)'%(first_id_chunk,last_id_chunk,last_id)):
            return

        ids = [data[i][0] for i in range(0,len(data)-1)]
        bf.write_data('id',uint32(ids))
        bf.reopen()
        ids = []
        if not check_and_update_task_info('writing float data row value (id: %d - %d of %d)'%(first_id_chunk,last_id_chunk,last_id)):
            return

        values = [data[i][1] for i in range(0,len(data)-1)]
        bf.write_data('value',float64(values))
        bf.reopen()
        values = []
        if not check_and_update_task_info('writing float data row variable_id (id: %d - %d of %d)'%(first_id_chunk,last_id_chunk,last_id)):
            return

        ids = [data[i][2] for i in range(0,len(data)-1)]
        # Remove None Values
        while ids.count(None):
            ids[ids.index(None)] = 0
        bf.write_data('variable_id',uint32(ids))
        bf.reopen()
        ids = []
        if not check_and_update_task_info('writing float data row time_id (id: %d - %d of %d)'%(first_id_chunk,last_id_chunk,last_id)):
            return

        ids = [data[i][3] for i in range(0,len(data)-1)]
        # Remove None Values
        while ids.count(None):
            ids[ids.index(None)] = 0
        bf.write_data('time_id',uint32(ids))
        bf.reopen()
        ids = []

    def _export_table_recorded_data_int():
        if not check_and_update_task_info('reading int data (id: %d - %d of %d)'%(first_id_chunk,last_id_chunk,last_id)):
            return

        data = list(RecordedDataInt.objects.filter(\
        id__range=(first_id_chunk,last_id_chunk)).values_list('id','value','variable_id','time_id'))
        if not check_and_update_task_info('writing int data row id (id: %d - %d of %d)'%(first_id_chunk,last_id_chunk,last_id)):
            return

        ids = [data[i][0] for i in range(0,len(data)-1)]
        bf.write_data('id',uint32(ids))
        bf.reopen()
        ids = []
        if not check_and_update_task_info('writing int data row value (id: %d - %d of %d)'%(first_id_chunk,last_id_chunk,last_id)):
            return

        values = [data[i][1] for i in range(0,len(data)-1)]
        bf.write_data('value',uint32(values))
        bf.reopen()
        values = []
        if not check_and_update_task_info('writing int data row variable_id (id: %d - %d of %d)'%(first_id_chunk,last_id_chunk,last_id)):
            return

        ids = [data[i][2] for i in range(0,len(data)-1)]
        # Remove None Values
        while ids.count(None):
            ids[ids.index(None)] = 0
        bf.write_data('variable_id',uint32(ids))
        bf.reopen()
        ids = []

        if not check_and_update_task_info('writing int data row time_id (id: %d - %d of %d)'%(first_id_chunk,last_id_chunk,last_id)):
            return

        ids = [data[i][3] for i in range(0,len(data)-1)]
        # Remove None Values
        while ids.count(None):
            ids[ids.index(None)] = 0
        bf.write_data('time_id',uint32(ids))
        bf.reopen()
        ids = []

    def _export_table_recorded_data_boolean():
        if not check_and_update_task_info('reading boolean data (id: %d - %d of %d)'%(first_id_chunk,last_id_chunk,last_id)):
            return

        data = list(RecordedDataBoolean.objects.filter(\
        id__range=(first_id_chunk,last_id_chunk)).values_list('id','value','variable_id','time_id'))
        if not check_and_update_task_info('writing boolean data row id (id: %d - %d of %d)'%(first_id_chunk,last_id_chunk,last_id)):
            return

        ids = [data[i][0] for i in range(0,len(data)-1)]
        bf.write_data('id',uint32(ids))
        bf.reopen()
        ids = []
        if not check_and_update_task_info('writing boolean data row value (id: %d - %d of %d)'%(first_id_chunk,last_id_chunk,last_id)):
            return

        values = [data[i][1] for i in range(0,len(data)-1)]
        bf.write_data('value',uint8(values))
        bf.reopen()
        values = []
        if not check_and_update_task_info('writing boolean data row variable_id (id: %d - %d of %d)'%(first_id_chunk,last_id_chunk,last_id)):
            return

        ids = [data[i][2] for i in range(0,len(data)-1)]
        bf.write_data('variable_id',uint32(ids))
        # Remove None Values
        while ids.count(None):
            ids[ids.index(None)] = 0
        bf.reopen()
        ids = []
        if not check_and_update_task_info('writing boolean data row time_id (id: %d - %d of %d)'%(first_id_chunk,last_id_chunk,last_id)):
            return

        ids = [data[i][3] for i in range(0,len(data)-1)]
        # Remove None Values
        while ids.count(None):
            ids[ids.index(None)] = 0
        bf.write_data('time_id',uint32(ids))
        bf.reopen()
        ids = []


    bf = mat_compatible_h5(filename)
    export = True
    last_id_chunk = first_id - 1

    while export:
        first_id_chunk = last_id_chunk + 1
        last_id_chunk  = first_id_chunk + chunk_size - 1
        if last_id_chunk > last_id:
            last_id_chunk = last_id
            export = False
        if check_and_update_task_info('next chunk id: %d - %d of %d'%(first_id_chunk,last_id_chunk,last_id)):
            tp.progress = tp.max-math.ceil((last_id-first_id_chunk)/chunk_size)
            tp.save()
        else:
            bf.close_file()
            tp.timestamp = time()
            tp.message = 'aborted'
            tp.failed = 1
            tp.save()
            return
        if table == 'RecordedDataFloat':
            _export_table_recorded_data_float()
        elif 	table == 'RecordedDataInt':
            _export_table_recorded_data_int()
        elif 	table == 'RecordedDataBoolean':
            _export_table_recorded_data_boolean()
        elif 	table == 'RecordedTime':
            _export_table_recorded_time()


    bf.close_file()
    tp.timestamp = time()
    tp.message = 'done'
    tp.done = 1
    tp.save()

def _cast_value(value,_type):
    '''
    cast value to _type
    '''
    if _type.upper() in ['FLOAT','FLOAT64','DOUBLE'] :
        return float64(value)
    elif _type.upper() in ['FLOAT32','SINGLE','REAL'] :
        return float32(value)
    elif  _type.upper() in ['INT32']:
        return int32(value)
    elif  _type.upper() in ['WORD','UINT','UINT16']:
        return uint16(value)
    elif  _type.upper() in ['INT16','INT']:
        return int16(value)
    elif _type.upper() in ['BOOL','BOOLEAN']:
        return uint8(value)
    else:
        return float64(value)
