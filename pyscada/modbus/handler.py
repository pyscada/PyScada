from pyscada.models import Client, ClientWriteTask
from pyscada.models import RecordedTime

from pyscada.modbus.client import Client as ModbusClient
from pyscada import log
from django.conf import settings

from time import time

class Handler:
    def __init__(self):
        if settings.PYSCADA_MODBUS.has_key('polling_interval'):
            self.dt_set = float(settings.PYSCADA_MODBUS['polling_interval'])
        else:
            self.dt_set = 5 # default value is 5 seconds
        self._clients   = {} # init client dict
        self._prepare_clients()

    def _prepare_clients(self):
        """
        prepare clients for query
        """
        for item in Client.objects.filter(active=1):
            if hasattr(item,'modbusclient'):
                self._clients[item.pk] = ModbusClient(item)


    def run(self):
        """
            request data
        """
        
        ## if there is something to write do it 
        self._do_write_task()

        ## data acquisition
        timestamp = RecordedTime(timestamp=time())
        timestamp.save()
        data = []
        for idx in self._clients:
            data += self._clients[idx].request_data(timestamp)
        
        return data
    
    
    
    def _do_write_task(self):
        """
        check for and do write tasks
        """
        
        for task in ClientWriteTask.objects.filter(done=False,start__lte=time(),failed=False):
            
            if self._clients[task.variable.client_id].write_data(task.variable.id,task.value): # do write task
                task.done=True
                task.fineshed=time()
                task.save()
                log.notice('changed variable %s (new value %1.6g %s)'%(task.variable.name,task.value,task.variable.unit.description),task.user)
            else:
                task.failed = True
                task.fineshed=time()
                task.save()
                log.error('change of variable %s failed'%(task.variable.name),task.user)
