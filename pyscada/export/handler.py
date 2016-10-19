#!/usr/bin/python
# -*- coding: utf-8 -*-
from pyscada import log
from pyscada.models import BackgroundTask
from pyscada.export.export import export_recordeddata_to_file
from pyscada.export.models import ScheduledExportTask, ExportTask


from django.conf import settings

from time import time, gmtime,strftime, mktime
from datetime import date,datetime, timedelta
from threading import Timer
import os

def _export_handler(job,today):
    
    if job.file_format.upper() == 'HDF5':
        file_ext    = '.h5'
    elif job.file_format.upper() == 'MAT':
        file_ext    = '.mat'
    elif job.file_format.upper() == 'CSV_EXCEL':
        file_ext    = '.csv'
    
    task_identifier=today.strftime('%Y%m%d')+'-%d'%job.pk
    bt = BackgroundTask(start=time(),\
        label='pyscada.export.export_measurement_data_%s'%task_identifier,\
        message='time waiting...',\
        timestamp=time(),\
        pid=str(os.getpid()),\
        identifier = task_identifier)
    bt.save()
    
    job.busy = True
    job.backgroundtask = bt
    job.save()

    
    export_recordeddata_to_file(\
        job.time_min,\
        job.time_max,\
        None,\
        job.variables.values_list('pk',flat=True),\
        file_ext,\
        filename_suffix=job.filename_suffix,\
        backgroundtask_id=bt.pk,\
        mean_value_period = job.mean_value_period)
    job.done     = True
    job.busy     = False
    job.fineshed = time()
    job.save()

    
class Handler:
    def __init__(self):
        '''
        
        '''
        self.dt_set = 5 # default value is every 5 seconds
        self._currend_day = gmtime().tm_yday
        
    def run(self):
        """
        this function will be called every self.dt_set seconds
            
        request data
            
        tm_wday 0=Monday 
        tm_yday   
        """
        today       = date.today()
        # only start new jobs after change the day changed
        if self._currend_day != gmtime().tm_yday:
            self._currend_day = gmtime().tm_yday
            for job in ScheduledExportTask.objects.filter(active=1): # get all active jobs
                
                add_task = False
                if job.export_period == 1: # daily
                    start_time      = '%s %02d:00:00'%((today - timedelta(1)).strftime('%d-%b-%Y'),job.day_time) # "%d-%b-%Y %H:%M:%S"
                    start_time      = mktime(datetime.strptime(start_time, "%d-%b-%Y %H:%M:%S").timetuple())
                    filename_suffix = 'daily_export_%d_%s'%(job.pk,job.label)
                    add_task = True
                elif job.export_period == 2 and time.gmtime().tm_yday%2 == 0: # on even days (2,4,...)
                    start_time      = '%s %02d:00:00'%((today - timedelta(2)).strftime('%d-%b-%Y'),job.day_time) # "%d-%b-%Y %H:%M:%S"
                    start_time      = mktime(datetime.strptime(start_time, "%d-%b-%Y %H:%M:%S").timetuple())
                    filename_suffix = 'two_day_export_%d_%s'%(job.pk,job.label)
                    add_task = True
                elif job.export_period == 7 and time.gmtime().tm_wday == 0: # on every monday
                    start_time      = '%s %02d:00:00'%((today - timedelta(7)).strftime('%d-%b-%Y'),job.day_time) # "%d-%b-%Y %H:%M:%S"
                    start_time      = mktime(datetime.strptime(start_time, "%d-%b-%Y %H:%M:%S").timetuple())
                    filename_suffix = 'weekly_export_%d_%s'%(job.pk,job.label)
                    add_task = True
                elif job.export_period == 14 and time.gmtime().tm_yday%14 == 0: # on every second monday
                    start_time      = '%s %02d:00:00'%((today - timedelta(14)).strftime('%d-%b-%Y'),job.day_time) # "%d-%b-%Y %H:%M:%S"
                    start_time      = mktime(datetime.strptime(start_time, "%d-%b-%Y %H:%M:%S").timetuple())
                    filename_suffix ='two_week_export_%d_%s'%(job.pk,job.label) 
                    add_task = True                 
                elif job.export_period == 30 and time.gmtime().tm_yday%30 == 0: # on every 30 days
                    start_time      = '%s %02d:00:00'%((today - timedelta(30)).strftime('%d-%b-%Y'),job.day_time) # "%d-%b-%Y %H:%M:%S"
                    start_time      = mktime(datetime.strptime(start_time, "%d-%b-%Y %H:%M:%S").timetuple())
                    filename_suffix = '30_day_export_%d_%s'%(job.pk,job.label)
                    add_task = True
                    
                if job.day_time == 0:
                    end_time    = '%s %02d:59:59'%((today - timedelta(1)).strftime('%d-%b-%Y'),23) # "%d-%b-%Y %H:%M:%S"
                else:
                    end_time    = '%s %02d:59:59'%(today.strftime('%d-%b-%Y'),job.day_time-1) # "%d-%b-%Y %H:%M:%S"
                end_time    = mktime(datetime.strptime(end_time, "%d-%b-%Y %H:%M:%S").timetuple())
                # create ExportTask
                if add_task:
                    if job.mean_value_period == 0:
                        mean_value_period = 5
                    else:
                        mean_value_period = job.mean_value_period
                    
                    et = ExportTask(\
                        label = filename_suffix,\
                        time_max = end_time,\
                        time_min=start_time,\
                        filename_suffix = filename_suffix,\
                        mean_value_period = mean_value_period,\
                        file_format = job.file_format,\
                        start = end_time+60\
                        )
                    et.save()
                    
                    et.variables.add(*job.variables.all())
                
                
        ## iter over all Export Tasks
        wait_time = 1 # wait one second to start the job 
        for job in ExportTask.objects.filter(done=False, busy=False, failed=False,start__lte=time()): # get all jobs
            log.debug(' started Timer %d'%job.pk)
            Timer(wait_time,_export_handler,[job,today]).start()
            job.busy = True
            job.save()
        
        ## delete all done jobs older the 60 days
        for job in ExportTask.objects.filter(done=True, busy=False, start__gte=time()+60*24*60*60):
            job.delete()
        ## delete all failed jobs older the 60 days
        for job in ExportTask.objects.filter(failed=True, start__gte=time()+60*24*60*60):
            job.delete()
        return None # because we have no data to store


