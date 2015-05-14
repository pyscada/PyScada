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
        self._cd = {}
        for d in self._f.values():
            self._d[d.name[1::]] = d
            if d.__class__.__name__ == "Group":
                for gm in d.values():
                    self._cd[gm.name[1::]] = gm

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
        elif dtype.str in ['<f4']:
            self._d[name].attrs['MATLAB_class'] = 'single'
        elif dtype.str in ['<i4']:
            self._d[name].attrs['MATLAB_class'] = 'int32'
        elif dtype.str in ['<u4']:
            self._d[name].attrs['MATLAB_class'] = 'uint32'
        elif dtype.str in ['<i2']:
            self._d[name].attrs['MATLAB_class'] = 'int16'
        elif dtype.str in ['<u2']:
            self._d[name].attrs['MATLAB_class'] = 'uint16'
        elif dtype.str in ['|u1']:
            self._d[name].attrs['MATLAB_class'] = 'uint8'
        return self._d[name]

    def create_group(self,name):
        self._d[name] = self._f.create_group(name)
        
    def create_complex_dataset(self,gname,dtype):
        CHUNCK      = 400
        GZIP_LEVEL  = 3
        if self._d.has_key(gname):
            return False
        self.create_group(gname)
        self._cd[gname+"/values"] = self._d[gname].create_dataset("values",
                                shape=(0,), dtype=dtype,maxshape=(None,),chunks=(CHUNCK,),
                                compression='gzip',compression_opts=GZIP_LEVEL)
                                
        self._cd[gname+"/time"] = self._d[gname].create_dataset("time",
                                shape=(0,), dtype="f8",maxshape=(None,),chunks=(CHUNCK,),
                                compression='gzip',compression_opts=GZIP_LEVEL)
        self._cd[gname+"/time"].attrs['MATLAB_class'] = 'double'
        if dtype.str in ['<f8']:
            self._cd[gname+"/values"].attrs['MATLAB_class'] = 'double'
        elif dtype.str in ['<f4']:
            self._cd[gname+"/values"].attrs['MATLAB_class'] = 'single'
        elif dtype.str in ['<i4']:
            self._cd[gname+"/values"].attrs['MATLAB_class'] = 'int32'
        elif dtype.str in ['<u4']:
            self._cd[gname+"/values"].attrs['MATLAB_class'] = 'uint32'
        elif dtype.str in ['<i2']:
            self._cd[gname+"/values"].attrs['MATLAB_class'] = 'int16'
        elif dtype.str in ['<u2']:
            self._cd[gname+"/values"].attrs['MATLAB_class'] = 'uint16'
        elif dtype.str in ['|u1']:
            self._cd[gname+"/values"].attrs['MATLAB_class'] = 'uint8'
        return self._d[gname]
        
    def write_data(self,name,data):
        self.create_dataset(name,data.dtype);
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

    def unix_time_stamp_to_matlab(timestamp):
        return (timestamp/86400)+719529
