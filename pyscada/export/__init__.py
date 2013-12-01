# -*- coding: utf-8 -*-
from pyscada.models import Variables
from pyscada.models import RecordedDataFloat
#from pyscada.models import RecordedDataInt
#from pyscada.models import RecordedDataBoolean
import scipy.io as sio
from datetime import timedelta
from datetime import datetime


"""
export measurements from the database to a file
"""

def datetime_to_matlab_datenum(dt):
    mdn = dt + timedelta(days = 366)
    frac = (dt-datetime(dt.year,dt.month,dt.day,0,0,0)).seconds / (24.0 * 60.0 * 60.0)
    return mdn.toordinal() + frac
def unix_time_stamp_to_matlab(timestamp):
    return (timestamp/86400)+719529
def export_database_to_mat(filename,time_id_min,time_id_max):
    vecData = {}
    vecData['time'] = [unix_time_stamp_to_matlab(element) for element in RecordedDataFloat.objects.time_data_column(time_id_min,time_id_max)]
    vcount = Variables.objects.filter(active=1).count()
    for val in Variables.objects.filter(active=1):
        tmp = RecordedDataFloat.objects.variable_data_column(val.pk,time_id_min,time_id_max)
        if len(tmp)>0:
            vecData[val.variable_name] = tmp
        vcount -= 1
        print(vcount)

    sio.savemat(filename, vecData)

