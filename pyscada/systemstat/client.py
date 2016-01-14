# -*- coding: utf-8 -*-
from pyscada.models import Client
from pyscada.utils import RecordData

from django.conf import settings
import psutil
from time import time

class Client:
    def __init__(self,client):
        self.variables  = []
        for var in client.variable_set.filter(active=1):
            if not hasattr(var,'systemstatvariable'):
                continue
            #self.variables[var.pk] = {'value_class':var.value_class,'record':var.record,'name':var.name,'inf_id':var.systemstatvariable.information,'param':var.systemstatvariable.parameter}
            self.variables.append(RecordData(var.pk,var.name,var.value_class,inf_id=var.systemstatvariable.information,param=var.systemstatvariable.parameter))
        
                
    def request_data(self,timestamp):
        '''
        (0,'cpu_percent'),
        (1,'virtual_memory_total'),
        (2,'virtual_memory_available'),
        (3,'virtual_memory_percent'),
        (4,'virtual_memory_used'),
        (5,'virtual_memory_free'),
        (6,'virtual_memory_active'),
        (7,'virtual_memory_inactive'),
        (8,'virtual_memory_buffers'),
        (9,'virtual_memory_cached'),
        (10,'swap_memory_total'),
        (11,'swap_memory_used'),
        (12,'swap_memory_free'),
        (13,'swap_memory_percent'),
        (14,'swap_memory_sin'),
        (15,'swap_memory_sout'),
        (17,'disk_usage_systemdisk_percent'),
        (18,'disk_usage_disk_percent'),
        '''
        data = {}
        for item in self.variables:
            if item.inf_id == 0:
                # cpu_percent
                if hasattr(psutil,'cpu_percent'):
                    value = psutil.cpu_percent()
            elif item.inf_id == 1:
                # virtual_memory_total
                if hasattr(psutil,'virtual_memory'):
                    value = psutil.virtual_memory().total
            elif item.inf_id == 2:
                #virtual_memory_available
                if hasattr(psutil,'virtual_memory'):
                    value = psutil.virtual_memory().available
            elif item.inf_id == 3:
                #virtual_memory_percent
                if hasattr(psutil,'virtual_memory'):
                    value = psutil.virtual_memory().percent
            elif item.inf_id == 4:
                #virtual_memory_used
                if hasattr(psutil,'virtual_memory'):
                    value = psutil.virtual_memory().used
            elif item.inf_id == 5:
                #virtual_memory_free
                if hasattr(psutil,'virtual_memory'):
                    value = psutil.virtual_memory().free
            elif item.inf_id == 6:
                #virtual_memory_active
                if hasattr(psutil,'virtual_memory'):
                    value = psutil.virtual_memory().active
            elif item.inf_id == 7:
                #virtual_memory_inactive
                if hasattr(psutil,'virtual_memory'):
                    value = psutil.virtual_memory().inactive
            elif item.inf_id == 8:
                #virtual_memory_buffers
                if hasattr(psutil,'virtual_memory'):
                    value = psutil.virtual_memory().buffers
            elif item.inf_id == 9:
                #virtual_memory_cached
                if hasattr(psutil,'virtual_memory'):
                    value = psutil.virtual_memory().cached
            elif item.inf_id == 10:
                #swap_memory_total
                if hasattr(psutil,'swap_memory'):
                    value = psutil.swap_memory().total
            elif item.inf_id == 11:
                #swap_memory_used
                if hasattr(psutil,'swap_memory'):
                    value = psutil.swap_memory().used
            elif item.inf_id == 12:
                #swap_memory_free
                if hasattr(psutil,'swap_memory'):
                    value = psutil.swap_memory().free
            elif item.inf_id == 13:
                #swap_memory_percent
                if hasattr(psutil,'swap_memory'):
                    value = psutil.swap_memory().percent
            elif item.inf_id == 14:
                #swap_memory_sin
                if hasattr(psutil,'swap_memory'):
                    value = psutil.swap_memory().sin
            elif item.inf_id == 15:
                #swap_memory_sout
                if hasattr(psutil,'swap_memory'):
                    value = psutil.swap_memory().sout
            elif item.inf_id == 17:
                #disk_usage_systemdisk_percent
                if hasattr(psutil,'disk_usage'):
                    value = psutil.disk_usage('/').percent
            elif item.inf_id == 18:
                #disk_usage_disk_percent
                if hasattr(psutil,'disk_usage'):
                    value = psutil.disk_usage(item.param).percent
            else:
                value = 0
            # update variable
            item.update_value(value,timestamp)
            
            
        return self.variables