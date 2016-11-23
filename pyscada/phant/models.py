# -*- coding: utf-8 -*-
from pyscada.models import Variable, Device
from pyscada.models import BackgroundTask

from django.db import models
import string, random


def gen_random_key(n=20):
    return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase) for _ in range(n))
        
class PhantDevice(models.Model):
    phant_device 		= models.OneToOneField(Device)
    public_key          = models.SlugField(max_length=20,default=gen_random_key,unique=True)
    private_key         = models.CharField(max_length=20,default=gen_random_key)
    
    