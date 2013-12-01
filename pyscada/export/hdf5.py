# -*- coding: utf-8 -*-
"""
Created on Sat Nov 30 14:22:58 2013

@author: martin schröder
"""
import os
import shutil
import h5py as h5

class mat:
    def __init__(self,filename):
        """


        """
        self.filename       = os.path.expanduser(filename)
        self.filepath       = []
        self._masterfilepath = os.path.abspath(os.path.dirname(__file__))
        self._masterfilename = "HDF5_MatlabMaster.h5"
        if not os.path.exists(self.filename):
            shutil.copyfile( os.path.join(self._masterfilepath,self._masterfilename),self.filename)
        self._f = []
        self.reopen()

    def close_file(self):
        if self._f:
            self._f.close();
    def reopen(self):
        self.close_file()
        self._f = h5.File(self.filename)
        self._d = {}
        for i in self._f.values():
            self._d[i.name[1::]] = i

    def __del__(self):
        self.close_file();

    def create_dataset(self,name,dtype):
        CHUNCK      = 400
        GZIP_LEVEL  = 3
        if self._d.has_key(name):
            return False
        self._d[name] = self._f.create_dataset(name,
                                shape=(0,), dtype=dtype,maxshape=(None,),chunks=(CHUNCK,),
                                compression='gzip',compression_opts=GZIP_LEVEL)
        if dtype.str in ['<f8']:
            self._d[name].attrs['MATLAB_class'] = 'double'
        elif dtype.str in ['<i4']:
            self._d[name].attrs['MATLAB_class'] = 'int32'
        elif dtype.str in ['|u1']:
            self._d[name].attrs['MATLAB_class'] = 'uint8'
        return self._d[name]


    def write_data(self,name,data):
        self.create_dataset(name,data.dtype);
        dl = self._d[name].len()
        self._d[name].resize((dl+data.size,))
        self._d[name][dl::] = data

    def batch_write(self,data_list):
        for i in data_list:
            self.write_data(i,data_list[i])

    def unix_time_stamp_to_matlab(timestamp):
        return (timestamp/86400)+719529