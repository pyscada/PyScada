# -*- coding: utf-8 -*-
from numpy import float64,int32,uint8
from pyscada.models import RecordedTime
from pyscada.models import RecordedDataFloat
from pyscada.models import RecordedDataInt
from pyscada.models import RecordedDataBoolean
from pyscada.models import ClientConfig
from pyscada.clients import modbus as mb
from time import time
class client():
    def __init__(self):
        self.clients        = {}
        self.client_config    = {}
        self.data             = {}
        self.prev_data        = {}
        self._prepare_clients()
        self.backup_data      = {}
    def _prepare_clients(self):
        """
        prepare clients for query
        """
        self.client_config    = ClientConfig.config.get_active_client_config()
        for idx in self.client_config:
            self.clients[idx] = mb.client(self.client_config[idx])


    def request(self):
        """
            request data
        """
        self.prev_data = self.data
        self.data = {}
        self.time = RecordedTime(timestamp=time())
        self.time.save()
        for idx in self.clients:
            self.data[idx] = self.clients[idx].request_data()
            if self.prev_data.has_key(idx):
                if not self.prev_data[idx]:
                    self.prev_data = {}



    def store(self):
        """
        save changed values to the database
        """
        count = 0
        dvf = []
        dvi = []
        dvb = []
        self.backup_data      = {}
        self.backup_data['time'] = (float64(self.time.timestamp)/86400)+719529
        for idx in self.data:
            if not self.data[idx]:
                continue
            for var_idx in self.data[idx]:
                variable_class = self.client_config[idx]['variable_input_config'][var_idx]['class']
                if self.prev_data.has_key(idx):
                    skip = (self.data[idx][var_idx] == self.prev_data[idx][var_idx])
                else:
                    skip = False
                # check for NaNs
                if (self.data[idx][var_idx] == "NaN"):
                    skip = True
                    value = 0
                else:
                    value = self.data[idx][var_idx]

                name = self.client_config[idx]['variable_input_config'][var_idx]['variable_name']
                if variable_class.upper() in ['FLOAT32','SINGLE','FLOAT','FLOAT64','REAL'] :
                    self.backup_data[name] = float64(value)
                elif  variable_class.upper() in ['INT32','INT16','INT','WORD','UINT','UINT16']:
                    self.backup_data[name] = int32(value)
                elif variable_class.upper() in ['BOOL']:
                    self.backup_data[name] = uint8(value)
                if skip:
                    count += 1
                else:
                    if variable_class.upper() in ['FLOAT32','SINGLE','FLOAT','FLOAT64','REAL'] :
                        dvf.append(RecordedDataFloat(time=self.time,variable_id=var_idx,value=self.data[idx][var_idx]))
                    elif variable_class.upper() in ['INT32','UINT32','INT16','INT','WORD','UINT','UINT16']:
                        dvi.append(RecordedDataInt(time=self.time,variable_id=var_idx,value=self.data[idx][var_idx]))
                    elif variable_class.upper() in ['BOOL']:
                        dvb.append(RecordedDataBoolean(time=self.time,variable_id=var_idx,value=self.data[idx][var_idx]))
        RecordedDataFloat.objects.bulk_create(dvf)
        RecordedDataInt.objects.bulk_create(dvi)
        RecordedDataBoolean.objects.bulk_create(dvb)
        #print(count)
        return True
