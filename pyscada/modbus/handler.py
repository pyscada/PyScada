from pyscada.models import Device, DeviceWriteTask
from pyscada.models import RecordedTime

from pyscada.modbus.device import Device as ModbusDevice
from pyscada import log
from django.conf import settings

from time import time

class Handler:
    def __init__(self):
        if settings.PYSCADA_MODBUS.has_key('polling_interval'):
            self.dt_set = float(settings.PYSCADA_MODBUS['polling_interval'])
        else:
            self.dt_set = 5 # default value is 5 seconds
        self._devices   = {} # init device dict
        self._prepare_devices()

    def _prepare_devices(self):
        """
        prepare devices for query
        """
        for item in Device.objects.filter(active=1):
            if hasattr(item,'modbusdevice'):
                self._devices[item.pk] = ModbusDevice(item)


    def run(self,timestamp=None):
        """
            request data
        """
        
        ## if there is something to write do it 
        self._do_write_task()

        ## data acquisition
        if timestamp is None:
            timestamp = RecordedTime(timestamp=time())
            timestamp.save()
        data = []
        for idx in self._devices:
            data += self._devices[idx].request_data(timestamp)
        
        return data
    
    
    
    def _do_write_task(self):
        """
        check for and do write tasks
        """
        
        for task in DeviceWriteTask.objects.filter(done=False,start__lte=time(),failed=False):
            if not task.variable.scaling is None:
                task.value = task.variable.scaling.scale_output_value(task.value)
            if self._devices.has_key(task.variable.device_id):
                if self._devices[task.variable.device_id].write_data(task.variable.id,task.value): # do write task
                    task.done=True
                    task.fineshed=time()
                    task.save()
                    log.notice('changed variable %s (new value %1.6g %s)'%(task.variable.name,task.value,task.variable.unit.description),task.user)
                else:
                    task.failed = True
                    task.fineshed=time()
                    task.save()
                    log.error('change of variable %s failed'%(task.variable.name),task.user)
            else:
                task.failed = True
                task.fineshed=time()
                task.save()
                log.error('device id not valid %d '%(task.variable.device_id),task.user)