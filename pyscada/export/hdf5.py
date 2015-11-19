# -*- coding: utf-8 -*-
"""
Created on Sat Nov 30 14:22:58 2013

@author: Martin Schröder
"""
import os
import io
import shutil
import h5py
import time


def unix_time_stamp_to_matlab_datenum(timestamp):
    '''
    convert dtype to maltab class string
    '''
    return (timestamp/86400)+719529
        
def dtype_to_matlab_class(dtype):
    '''
    convert dtype to maltab class string
    '''
    if dtype.str in ['<f8']:
        return 'double'
    elif dtype.str in ['<f4']:
        return 'single'
    elif dtype.str in ['<i8']:
        return 'int64'
    elif dtype.str in ['<u8']:
        return 'uint64'
    elif dtype.str in ['<i4']:
        return 'int32'
    elif dtype.str in ['<u4']:
        return 'uint32'
    elif dtype.str in ['<i2']:
        return 'int16'
    elif dtype.str in ['<u2']:
        return 'uint16'
    elif dtype.str in ['|i1']:
        return 'int8'
    elif dtype.str in ['|u1']:
        return 'uint8'

class mat_compatible_h5:
    def __init__(self,filename,**kwargs):
        """


        """
        self.filename       = os.path.expanduser(filename)
        self.filepath       = []
        self.CHUNCK         = 4320 # 12V/Min * 60 Min/Hour * 6 Hours (1/4 Day)
        self.GZIP_LEVEL     = 3
        if not os.path.exists(self.filename):
            self.create_file()
        else:
            self.open_file()

        for key, value in kwargs.iteritems():
            if isinstance(value,basestring): 
                self._f.attrs[key] = value
            else:
                self._f.attrs[key] = value.__str__()
        self.reopen()

    def create_file(self):
        self._f = h5py.File(self.filename,'w',userblock_size=512)
        self._f.close()
        userblock_data = 'MATLAB 7.3 MAT-file, Platform: PCWIN64, Created on: %s HDF5 schema 1.00 .'%time.strftime('%a %b %d %H:%M:%S %Y')
        while len(userblock_data)< 116:
            userblock_data += ' '
        userblock_data += chr(0)*9
        userblock_data += 'IM';
        with io.open(self.filename,'rb+') as f:
            f.write(userblock_data)
        self.reopen()

    def close_file(self):
        if self._f:
            self._f.close();
    def reopen(self):
        self.close_file()
        self.open_file()
    def open_file(self):
        self._f = h5py.File(self.filename,'w')
        self._d = {}
        self._cd = {}
        for d in self._f.values():
            self._d[d.name[1::]] = d
            if d.__class__.__name__ == "Group":
                for gm in d.values():
                    self._cd[gm.name[1::]] = gm
    def __del__(self):
        self.close_file();

    def create_dataset(self,name,dtype):
        if self._d.has_key(name):
            return False
        self._d[name] = self._f.create_dataset(name,
                                shape=(0,), dtype=dtype,maxshape=(None,),chunks=(self.CHUNCK,),
                                compression='gzip',compression_opts=self.GZIP_LEVEL)
        self._d[name].attrs['MATLAB_class'] = dtype_to_matlab_class(dtype)
        return self._d[name]

    def create_group(self,name):
        self._d[name] = self._f.create_group(name)

    def create_complex_dataset(self,gname,dtype):
        if self._d.has_key(gname):
            return False
        self.create_group(gname)
        self._cd[gname+"/values"] = self._d[gname].create_dataset("values",
                                shape=(0,), dtype=dtype,maxshape=(None,),chunks=(self.CHUNCK,),
                                compression='gzip',compression_opts=self.GZIP_LEVEL)

        self._cd[gname+"/time"] = self._d[gname].create_dataset("time",
                                shape=(0,), dtype="f8",maxshape=(None,),chunks=(self.CHUNCK,),
                                compression='gzip',compression_opts=self.GZIP_LEVEL)
        self._cd[gname+"/time"].attrs['MATLAB_class'] = 'double'
        self._cd[gname+"/values"].attrs['MATLAB_class'] = dtype_to_matlab_class(dtype)
        return True

    def write_data(self,name,data,**kwargs):
        if self.create_dataset(name,data.dtype):
            for key, value in kwargs.iteritems():
                if isinstance(value,basestring): 
                    self._d[name].attrs[key] = value
                else:
                    self._d[name].attrs[key] = value.__str__()

        dl = self._d[name].len()
        self._d[name].resize((dl+data.size,))
        self._d[name][dl::] = data

    def write_complex_data(self,gname,data,times):
        self.create_complex_dataset(gname,data.dtype);
        dl = self._cd[gname+"/values"].len()
        self._cd[gname + "/values"].resize((dl+data.size,))
        self._cd[gname+"/time"].resize((dl+data.size,))
        self._cd[gname+"/values"][dl::] = data
        self._cd[gname+"/time"][dl::] = times

    def batch_write(self,data_list):
        for name in data_list:
            self.write_data(name,data_list[name])

    def batch_complex_write(self,data_list):
        times = data_list.pop("time")
        self.write_data("time",times)
        for name in data_list:
            self.write_complex_data(name,data_list[name],times)

    
    