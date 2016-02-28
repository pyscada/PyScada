# -*- coding: utf-8 -*-
from pyscada.models import Device
from django.conf import settings
try:
    import psutil
    driver_ok = True
except ImportError:
    driver_ok = False
    
    
from time import time

class Device:
    def __init__(self,device):
        self.variables  = []
        for var in device.variable_set.filter(active=1):
            if not hasattr(var,'systemstatvariable'):
                continue
            self.variables.append(var)
            
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
        if not driver_ok:
            return None
        
        output = []
        for item in self.variables:
            if item.systemstatvariable.information == 0:
                # cpu_percent
                if hasattr(psutil,'cpu_percent'):
                    value = psutil.cpu_percent()
            elif item.systemstatvariable.information == 1:
                # virtual_memory_total
                if hasattr(psutil,'virtual_memory'):
                    value = psutil.virtual_memory().total
            elif item.systemstatvariable.information == 2:
                #virtual_memory_available
                if hasattr(psutil,'virtual_memory'):
                    value = psutil.virtual_memory().available
            elif item.systemstatvariable.information == 3:
                #virtual_memory_percent
                if hasattr(psutil,'virtual_memory'):
                    value = psutil.virtual_memory().percent
            elif item.systemstatvariable.information == 4:
                #virtual_memory_used
                if hasattr(psutil,'virtual_memory'):
                    value = psutil.virtual_memory().used
            elif item.systemstatvariable.information == 5:
                #virtual_memory_free
                if hasattr(psutil,'virtual_memory'):
                    value = psutil.virtual_memory().free
            elif item.systemstatvariable.information == 6:
                #virtual_memory_active
                if hasattr(psutil,'virtual_memory'):
                    value = psutil.virtual_memory().active
            elif item.systemstatvariable.information == 7:
                #virtual_memory_inactive
                if hasattr(psutil,'virtual_memory'):
                    value = psutil.virtual_memory().inactive
            elif item.systemstatvariable.information == 8:
                #virtual_memory_buffers
                if hasattr(psutil,'virtual_memory'):
                    value = psutil.virtual_memory().buffers
            elif item.systemstatvariable.information == 9:
                #virtual_memory_cached
                if hasattr(psutil,'virtual_memory'):
                    value = psutil.virtual_memory().cached
            elif item.systemstatvariable.information == 10:
                #swap_memory_total
                if hasattr(psutil,'swap_memory'):
                    value = psutil.swap_memory().total
            elif item.systemstatvariable.information == 11:
                #swap_memory_used
                if hasattr(psutil,'swap_memory'):
                    value = psutil.swap_memory().used
            elif item.systemstatvariable.information == 12:
                #swap_memory_free
                if hasattr(psutil,'swap_memory'):
                    value = psutil.swap_memory().free
            elif item.systemstatvariable.information == 13:
                #swap_memory_percent
                if hasattr(psutil,'swap_memory'):
                    value = psutil.swap_memory().percent
            elif item.systemstatvariable.information == 14:
                #swap_memory_sin
                if hasattr(psutil,'swap_memory'):
                    value = psutil.swap_memory().sin
            elif item.systemstatvariable.information == 15:
                #swap_memory_sout
                if hasattr(psutil,'swap_memory'):
                    value = psutil.swap_memory().sout
            elif item.systemstatvariable.information == 17:
                #disk_usage_systemdisk_percent
                if hasattr(psutil,'disk_usage'):
                    value = psutil.disk_usage('/').percent
            elif item.systemstatvariable.information == 18:
                #disk_usage_disk_percent
                if hasattr(psutil,'disk_usage'):
                    value = psutil.disk_usage(item.systemstatvariable.parameter).percent
            else:
                value = 0
            # update variable
            if item.update_value(value,timestamp):
                output.append(item.create_recorded_data_element())
            
            
        return output