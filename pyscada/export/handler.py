#!/usr/bin/python
# -*- coding: utf-8 -*-
from pyscada.export import export_measurement_data_to_file
from pyscada.export.models import ExportJob
from django.conf import settings

from time import time, gmtime,strftime
from datetime import date,datetime, timedelta
from threading import Timer

def export_task(export_job):
    '''
    handle the export job 
    '''
    passa


class Handler:
    def __init__(self):
        '''
        
        '''
        self.dt_set = 10 # default value is every 10 seconds
        self._currend_day = gmtime().tm_yday
        
    def run(self):
        """
        this function will be called every self.dt_set seconds
            
        request data
            
        tm_wday 0=Monday 
        tm_yday   
        """
        # only start new jobs after change the day changed
        if self._currend_day != gmtime().tm_yday:
            self._currend_day = gmtime().tm_yday
            for job in ExportJob.objects.filter(active=1): # get all active jobs
                wait_time   = job.day_time * 3600 # time to wait for execution
                active_vars = job.variables.values_list('pk',flat=True)
                today       = date.today()
                end_time    = '%s %02d:59:59'%(today.strftime('%d-%b-%Y'),23 - job.day_time) # "%d-%b-%Y %H:%M:%S"
                if job.file_format.upper() == 'HDF5':
                    file_ext    = '.h5'
                elif job.file_format.upper() == 'MAT':
                    file_ext    = '.mat'
                elif job.file_format.upper() == 'CSV_EXCEL':
                    file_ext    = '.csv'
                if job.export_period == 1: # daily
                    start_time  = '%s %02d:00:00'%((today - timedelta(1)).strftime('%d-%b-%Y'),job.day_time) # "%d-%b-%Y %H:%M:%S"
                    # create timerobject
                    Timer(wait_time,export_measurement_data_to_file,[start_time,None,end_time,active_vars,file_ext],\
                        {'filename_suffix':'daily_export_%d'%job.pk,'task_identifier':today.strftime('%Y%m%d')+'-%d'%job.pk}).start()
                elif job.export_period == 2 and time.gmtime().tm_yday%2 == 0: # on even days (2,4,...)
                    start_time  = '%s %02d:00:00'%((today - timedelta(2)).strftime('%d-%b-%Y'),job.day_time) # "%d-%b-%Y %H:%M:%S"
                    # create timerobject
                    Timer(wait_time,export_measurement_data_to_file,[start_time,None,end_time,active_vars,file_ext],\
                        {'filename_suffix':'two_day_export_%d'%job.pk,'task_identifier':today.strftime('%Y%m%d')+'-%d'%job.pk}).start()
                elif job.export_period == 7 and time.gmtime().tm_wday == 0: # on every monday
                    start_time  = '%s %02d:00:00'%((today - timedelta(7)).strftime('%d-%b-%Y'),job.day_time) # "%d-%b-%Y %H:%M:%S"
                    # create timerobject
                    Timer(wait_time,export_measurement_data_to_file,[start_time,None,end_time,active_vars,file_ext],\
                        {'filename_suffix':'weekly_export_%d'%job.pk,'task_identifier':today.strftime('%Y%m%d')+'-%d'%job.pk}).start()
                elif job.export_period == 14 and time.gmtime().tm_yday%14 == 0: # on every second monday
                    start_time  = '%s %02d:00:00'%((today - timedelta(14)).strftime('%d-%b-%Y'),job.day_time) # "%d-%b-%Y %H:%M:%S"
                    # create timerobject
                    Timer(wait_time,export_measurement_data_to_file,[start_time,None,end_time,active_vars,file_ext],\
                        {'filename_suffix':'two_week_export_%d'%job.pk,'task_identifier':today.strftime('%Y%m%d')+'-%d'%job.pk}).start()
                elif job.export_period == 30 and time.gmtime().tm_yday%30 == 0: # on every 30 days
                    start_time  = '%s %02d:00:00'%((today - timedelta(30)).strftime('%d-%b-%Y'),job.day_time) # "%d-%b-%Y %H:%M:%S"
                    # create timerobject
                    Timer(wait_time,export_measurement_data_to_file,[start_time,None,end_time,active_vars,file_ext],\
                        {'filename_suffix':'30_day_export_%d'%job.pk,'task_identifier':today.strftime('%Y%m%d')+'-%d'%job.pk}).start()

        return None # because we have no data to store
