# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.models import Device, Variable

from django.db import models
from django.utils.encoding import python_2_unicode_compatible

import string
import random
import logging

logger = logging.getLogger(__name__)


def gen_random_key(n=20):
    # todo avoid collisions on public_key field
    return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase) for _ in range(n))


@python_2_unicode_compatible
class PhantDevice(models.Model):
    phant_device = models.OneToOneField(Device)
    public_key = models.SlugField(max_length=20, default=gen_random_key, unique=True)
    private_key = models.CharField(max_length=20, default=gen_random_key)

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
