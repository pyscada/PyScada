# -*- coding: utf-8 -*-
from pyscada.models import Variable,BackgroundTask

from django.db import models
from django.contrib.auth.models import User

import time
from datetime import datetime
from pytz import UTC
#
# Model
#

def datetime_now():
    return datetime.now(UTC)

class ScheduledExportTask(models.Model):
    id 				= models.AutoField(primary_key=True)
    label			= models.CharField(max_length=400, default='')
    variables		= models.ManyToManyField(Variable)
    day_time_choices = [(x,'%d:00'%x) for x in range(0,24)]
    day_time        = models.PositiveSmallIntegerField(default=0,choices=day_time_choices,help_text='day time wenn the job will be started in UTC')
    mean_value_period = models.PositiveSmallIntegerField(default=0,help_text='in Seconds (0 = no mean value)')
    active		    = models.BooleanField(default=False,blank=True,  help_text='to activate scheduled export')
    file_format_choices = (('hdf5','Hierarchical Data Format Version 5'),('mat','Matlab® mat v7.3 compatible file'),('CSV_EXCEL','Microsoft® Excel® compatible csv file'))
    file_format     = models.CharField(max_length=400, default='hdf5',choices=file_format_choices)
    export_period_choices = ((1,'1 Day'),(2,'2 Days (on every even Day of the year)'),(7,'7 Days (on Mondays)'),(14,'14 Days'),(30,'30 Days'))
    export_period = models.PositiveSmallIntegerField(default=0,choices=export_period_choices,help_text='')
    def __unicode__(self):
        return unicode(self.label)


class ExportTask(models.Model):
    id 				= models.AutoField(primary_key=True)
    label			= models.CharField(max_length=400, default='None',blank=True)
    backgroundtask	= models.ForeignKey(BackgroundTask,null=True,blank=True, on_delete=models.SET_NULL)
    variables		= models.ManyToManyField(Variable)
    mean_value_period = models.PositiveSmallIntegerField(default=0,help_text='in Seconds (0 = no mean value)')
    file_format_choices = (('hdf5','Hierarchical Data Format Version 5'),('mat','Matlab® mat v7.3 compatible file'),('CSV_EXCEL','Microsoft® Excel® compatible csv file'))
    file_format     = models.CharField(max_length=400, default='hdf5',choices=file_format_choices)
    filename_suffix = models.CharField(max_length=400, default='',blank=True)
    datetime_min    = models.DateTimeField(default=None, null=True)
    datetime_max    = models.DateTimeField(default=None, null=True)
    user	 		    = models.ForeignKey(User,null=True,blank=True, on_delete=models.SET_NULL)
    datetime_start  = models.DateTimeField(default=datetime_now)
    datetime_fineshed = models.DateTimeField(null=True,blank=True)
    done			= models.BooleanField(default=False,blank=True) # label task has been done
    busy            = models.BooleanField(default=False,blank=True) # label task is in operation done
    failed			= models.BooleanField(default=False,blank=True) # label task has failed
    def __unicode__(self):
        return unicode(self.label)
    
    def time_min(self):
        return time.mktime(self.datetime_min.timetuple())
    def time_max(self):
        return time.mktime(self.datetime_max.timetuple())
    def start(self):
        return time.mktime(self.datetime_start.timetuple())
    def fineshed(self):
        return time.mktime(self.datetime_fineshed.timetuple())

'''
class ExportFile(models.Model):
    id 			= models.AutoField(primary_key=True)
    exporttask	= models.ForeignKey(ExportTask,null=True, on_delete=models.SET_NULL)
    filename    = models.FilePathField()
''' 
