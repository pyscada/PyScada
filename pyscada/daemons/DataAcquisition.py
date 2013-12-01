# -*- coding: utf-8 -*-

import threading
import os,sys
from time import time, localtime, strftime
from pyscada.models import GlobalConfig
from pyscada.clients import client
from pyscada.export.hdf5 import mat


class DataAcquisition():
    def __init__(self):
        self._dt        = GlobalConfig.objects.get_value_by_key('stepsize')
        self._cl        = client()                  # init a client Instance for field data query
        self._backup_file_name = 'measurement_data' # name of the backupfile
        self._backup_file_path = os.path.expanduser('~/measurement_data') # default path to store the backupfiles
        if not os.path.exists(self._backup_file_path ):
            os.mkdir(self._backup_file_path)
        self._backup_thread     = []
        self._query_thread      = []    
        self._bf                = []
        self._new_file_timer    = []
        self._new_backupfile()
        self._run = True
        self._query_timer = threading.Timer(0.1,self.run)
        self._query_timer.start()
        
        
    def run(self):
        # first get the next start time
        tic = time()
        # second start the query thread
        self._query_thread = threading.Thread(target=self._query_data)
        self._query_thread.start()
        self._query_thread.join(float(self._dt)*2)
        # third set the next start of querying data
        dt = float(self._dt) - (time()-tic)
        if dt<0:
            dt = 0.1
        if self._run:
            self._query_timer = threading.Timer(dt,self.run)
            self._query_timer.start()
        # fourth start the backup thread
        if self._backup_thread:
            # if backup is running wait until is finished
            self._backup_thread.join()
        self._backup_thread = threading.Thread(target=self._backup_data,args=[self._cl.backup_data])
        self._backup_thread.start()
        
    def _query_data(self):
        self._cl.request();
        self._cl.store();

    def _backup_data(self,data):
        self._bf.batch_write(data)
        self._bf.reopen()

    def _new_backupfile(self):
        """
        trigger a new backupfile
        """
        # trigger a new file once a day at 24:00
        if self._new_file_timer:
            self._new_file_timer.cancel()
        dt = time()/(24*60*60)
        dt = (round(dt)+1-dt)*(24*60*60)
        self._new_file_timer = threading.Timer(dt,self._new_backupfile)
        self._new_file_timer.start()
        if self._backup_thread:
            # if backuo is running wait until is finished
            self._backup_thread.join()
        if self._bf:
            self._bf.close_file()
            self._bf = []
        cdstr = strftime("%Y_%m_%d_%H%M",localtime())
        filename = self._backup_file_name + '_' + cdstr + '.mat'
        self._bf = mat(os.path.join(self._backup_file_path,filename))
    

    def __del__(self):
        self._run = False
        if  self._backup_thread:
            self._backup_thread.join()
        if self._new_file_timer:
            self._new_file_timer.cancel()
        if self._query_thread:
            self._query_thread.join()