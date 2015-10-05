# -*- coding: utf-8 -*-
from pyscada import log
from pyscada.models import Client
from pyscada.models import Variable
from pyscada.models import RecordedTime
from pyscada.models import RecordedDataFloat
from pyscada.models import RecordedDataInt
from pyscada.models import RecordedDataBoolean
from pyscada.models import RecordedDataCache
from django.conf import settings
import psutil
from time import time

class client:
    def __init__(self,client):
        self.variables  = {}
        self._variable_config   = self._prepare_variable_config(client)
        

    def _prepare_variable_config(self,client):
        
        for var in client.variable_set.filter(active=1):
            if not hasattr(var,'systemstatvariable'):
                continue
            self.variables[var.pk] = {'value_class':var.value_class,'record':var.record,'name':var.name,'inf_id':var.systemstatvariable.information,'param':var.systemstatvariable.parameter}

        
    def request_data(self):
        '''
        (0,'cpu_percent'),
        (1,'phymem_usage_total'),
        (2,'phymem_usage_available'),
        (3,'phymem_usage_percent'),
        (4,'phymem_usage_used'),
        (5,'phymem_usage_free'),
        (6,'phymem_usage_active'),
        (7,'phymem_usage_inactive'),
        (8,'phymem_usage_buffers'),
        (9,'phymem_usage_cached'),
        (10,'swap_memory_total'),
        (11,'swap_memory_used'),
        (12,'swap_memory_free'),
        (13,'swap_memory_percent'),
        (14,'swap_memory_sin'),
        (15,'swap_memory_sout'),
        (16,'cached_phymem'),
        (17,'disk_usage_systemdisk'),
        '''
        data = {}
        for key,item in self.variables.iteritems():
            if item['inf_id'] == 0:
                # cpu_percent
                value = psutil.cpu_percent()
            elif item['inf_id'] == 1:
                # phymem_usage_total
                value = psutil.phymem_usage().total
            elif item['inf_id'] == 2:
                #phymem_usage_available
                value = psutil.phymem_usage().available
            elif item['inf_id'] == 3:
                #phymem_usage_percent
                value = psutil.phymem_usage().percent
            elif item['inf_id'] == 4:
                #phymem_usage_used
                value = psutil.phymem_usage().used
            elif item['inf_id'] == 5:
                #phymem_usage_free
                value = psutil.phymem_usage().free
            elif item['inf_id'] == 6:
                #phymem_usage_active
                value = psutil.phymem_usage().active
            elif item['inf_id'] == 7:
                #phymem_usage_inactive
                value = psutil.phymem_usage().inactive
            elif item['inf_id'] == 8:
                #phymem_usage_buffers
                value = psutil.phymem_usage().buffers
            elif item['inf_id'] == 9:
                #phymem_usage_cached
                value = psutil.phymem_usage().cached
            elif item['inf_id'] == 10:
                #swap_memory_total
                value = psutil.swap_memory().total
            elif item['inf_id'] == 11:
                #swap_memory_used
                value = psutil.swap_memory().used
            elif item['inf_id'] == 12:
                #swap_memory_free
                value = psutil.swap_memory().free
            elif item['inf_id'] == 13:
                #swap_memory_percent
                value = psutil.swap_memory().percent
            elif item['inf_id'] == 14:
                #swap_memory_sin
                value = psutil.swap_memory().sin
            elif item['inf_id'] == 15:
                #swap_memory_sout
                value = psutil.swap_memory().sout
            elif item['inf_id'] == 16:
                #cached_phymem
                value = psutil.cached_phymem()
            elif item['inf_id'] == 17:
                #disk_usage_systemdisk
                value = psutil.disk_usage('/')
            elif item['inf_id'] == 18:
                #disk_usage_systemdisk
                value = psutil.disk_usage(item['param'])
            else:
                value = 0
            data[key] = value
            
            
        return data