# -*- coding: utf-8 -*-
import threading
import os
from time import time, localtime, strftime

from pyscada.models import GlobalConfig
from pyscada.clients import client
from pyscada.export.hdf5 import mat



class DataAcquisition():
    def __init__(self):
        # time in seconds between the measurement
        self._dt        = GlobalConfig.objects.get_value_by_key('stepsize')
        self._s         = -1                        # status of the service
        self._cl        = client()                  # init a client Instance for field data query
        self._backup_file_name = 'measurement_data' # name of the backupfile
        self._backup_file_path = os.path.expanduser('~/measurement_data') # default path to store the backupfiles
        if not os.path.exists(self._backup_file_path ):
            os.mkdir(self._backup_file_path)
        self._backup_thread = []
        self._query_thread = []    
        self._bf        = []
        self._new_file_timer = []
        self._new_backupfile()


    def _reinit(self):
        self._s   = 1                 # status of the service
        self._cl  = client()          # reinit a client Instance for field data query
        self._dt  = GlobalConfig.objects.get_value_by_key('stepsize')
        self._new_backupfile()
        self.service()

    def service(self):
        if self._s == 1:
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

            self._query_timer = threading.Timer(dt,self.service)
            self._query_timer.start()
            # fourth start the backup thread
            if self._backup_thread:
                # if backup is running wait until is finished
                self._backup_thread.join()
            self._backup_thread = threading.Thread(target=self._backup_data,args=[self._cl.backup_data])
            self._backup_thread.start()


        elif self._s == 2:
            self._reinit()
        else:
            self._s = -1
            print "stopped Logging"

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
            self._new_file_timer.cancle()
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

    def status(self):
        """
        print the service status
        """
        if self._s == -1:
            print("stopped")
        elif self._s == 0:
            print("stopping")
        elif self._s == 1:
            print("running")
        elif self._s == 2:
            print("restart")
        else:
            print("unknown status")

    def start(self):
        """ start the DataAcquisition service

        """
        if self._s == -1:
            self._s = 1
            print "start logging"
            self.service()
        else:
            self.status()

    def stop(self):
        """ stop the DataAcquisition service

        """
        self._s = 0

    def restart(self):
        self._s   = 2                 # status of the service
        
    def __del__(self):
        self.stop()
        if  self._backup_thread:
            self._backup_thread.join()
        if self._new_file_timer:
            self._new_file_timer.cancle()
        if self._query_thread:
            self._query_thread.join()
        self.status   
            