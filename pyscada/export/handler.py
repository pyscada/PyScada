#!/usr/bin/python
# -*- coding: utf-8 -*-
from pyscada.export import export_measurement_data_to_h5

from django.conf import settings

from time import time

class Handler:
    def __init__(self):
        '''
        
        '''
        self.dt_set = 5 # default value is 5 seconds
        self._export_interval = 24*60*60 # 1 Day
        self._old_time = time()
        
    def run(self):
        """
            this function will be called every self.dt_set seconds
            
            request data
        """
        if time() > self._old_time + self._export_interval:
            self._old_time = time()
            export_measurement_data_to_h5()
        
        return None
