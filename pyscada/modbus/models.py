# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.models import Device
from pyscada.models import Variable
from . import PROTOCOL_ID

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
import logging

logger = logging.getLogger(__name__)


@python_2_unicode_compatible
class ModbusDevice(models.Model):
    modbus_device = models.OneToOneField(Device, on_delete=models.CASCADE)
    protocol_choices = ((0, 'TCP'), (1, 'UDP'), (2, 'serial ASCII'), (3, 'serial RTU'), (4, 'serial Binary'),)
    protocol = models.PositiveSmallIntegerField(default=0, choices=protocol_choices)
    framer_choices = ((0, 'Socket'), (1, 'RTU'), (2, 'ASCII'), (3, 'Binary'),)
    framer = models.PositiveSmallIntegerField(null=True, blank=True, choices=framer_choices)
    ip_address = models.GenericIPAddressField(default='127.0.0.1')
    port = models.CharField(default='502',
                            max_length=400,
                            help_text="for TCP and UDP enter network port as number "
                                      "(def. 502, for serial ASCII and RTU enter serial port (/dev/pts/13))")
    unit_id = models.PositiveSmallIntegerField(default=0)
    timeout = models.PositiveSmallIntegerField(default=0, help_text="0 use default, else value in seconds")
    stopbits_choices = ((0, 'default'), (1, 'one stopbit'), (2, '2 stopbits'),)
    stopbits = models.PositiveSmallIntegerField(default=0, choices=stopbits_choices)
    bytesize_choices = ((0, 'default'), (5, 'FIVEBITS'), (6, 'SIXBITS'), (7, 'SEVENBITS'), (8, 'EIGHTBITS'),)
    bytesize = models.PositiveSmallIntegerField(default=0, choices=bytesize_choices)
    parity_choices = ((0, 'default'), (1, 'NONE'), (2, 'EVEN'), (3, 'ODD'),)
    parity = models.PositiveSmallIntegerField(default=0, choices=parity_choices)
    baudrate = models.PositiveSmallIntegerField(default=0, help_text="0 use default")

    protocol_id = PROTOCOL_ID

    def parent_device(self):
        try:
            return self.modbus_device
        except:
            return None

    def __str__(self):
        return self.modbus_device.short_name


@python_2_unicode_compatible
class ModbusVariable(models.Model):
    modbus_variable = models.OneToOneField(Variable, on_delete=models.CASCADE)
    address = models.PositiveIntegerField()
    function_code_read_choices = (
        (0, 'not selected'), (1, 'coils (FC1)'), (2, 'discrete inputs (FC2)'), (3, 'holding registers (FC3)'),
        (4, 'input registers (FC4)'))
    function_code_read = models.PositiveSmallIntegerField(default=0, choices=function_code_read_choices, help_text="")

    protocol_id = PROTOCOL_ID

    def __str__(self):
        return self.modbus_variable.short_name


class ExtendedModbusDevice(Device):
    class Meta:
        proxy = True
        verbose_name = 'Modbus Device'
        verbose_name_plural = 'Modbus Devices'


class ExtendedModbusVariable(Variable):
    class Meta:
        proxy = True
        verbose_name = 'Modbus Variable'
        verbose_name_plural = 'Modbus Variables'
