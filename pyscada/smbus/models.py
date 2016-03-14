from pyscada.models import Device
from pyscada.models import Variable

from django.db import models

class SMbusDevice(models.Model):
    smbus_device 		= models.OneToOneField(Device)
    device_type_choises = (('ups_pico','UPS PIco'),)
    device_type         = models.CharField(max_length=400,choices=device_type_choises)                
    port				= models.CharField(default='1',max_length=400,)
    address_choices     = [(i,'0x%s/%d'%(hex(i),i)) for i in xrange(256)]
    address  			= models.PositiveSmallIntegerField(default=None,choices=address_choices,null=True)
    def __unicode__(self):
        return unicode(self.smbus_device.short_name)
    
class SMbusVariable(models.Model):
    smbus_variable 				= models.OneToOneField(Variable)
    information                 = models.CharField(default='None',max_length=400,)