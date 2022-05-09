# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.models import Device, Variable
from . import PROTOCOL_ID

from django.db import models

import string
import random
import logging

logger = logging.getLogger(__name__)


def gen_random_key(n=20):
    # todo avoid collisions on public_key field
    return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase) for _ in range(n))


class PhantDevice(models.Model):
    phant_device = models.OneToOneField(Device, on_delete=models.CASCADE)
    public_key = models.SlugField(max_length=20, default=gen_random_key, unique=True)
    private_key = models.CharField(max_length=20, default=gen_random_key)

    protocol_id = PROTOCOL_ID

    def parent_device(self):
        try:
            return self.phant_device
        except:
            return None

    def __str__(self):
        return self.phant_device.short_name


class ExtendedPhantDevice(Device):
    class Meta:
        proxy = True
        verbose_name = 'Phant Device'
        verbose_name_plural = 'Phant Devices'


class ExtendedPhantVariable(Variable):
    class Meta:
        proxy = True
        verbose_name = 'Phant Variable'
        verbose_name_plural = 'Phant Variables'
