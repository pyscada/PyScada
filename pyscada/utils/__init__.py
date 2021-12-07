#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.six import integer_types

import re
from datetime import datetime
from pytz import UTC
import numpy as np
from django.utils.timezone import now
import logging
logger = logging.getLogger(__name__)


def extract_numbers_from_str(value_str):
    match = re.match(r"(([^0-9,^-]+)?)(?P<number>-?[0-9]+[.]?[0-9]+)", value_str, re.I)
    if match:
        match = match.groupdict()
        return float(match['number'])
    else:
        return None


def decode_bcd(values):
    """
    decode bcd as int to dec
    """

    bin_str_out = ''
    if isinstance(values, integer_types):
        bin_str_out = bin(values)[2:].zfill(16)
        bin_str_out = bin_str_out[::-1]
    else:
        for value in values:
            bin_str = bin(value)[2:].zfill(16)
            bin_str = bin_str[::-1]
            bin_str_out = bin_str + bin_str_out

    dec_num = 0
    for i in range(len(bin_str_out) / 4):
        bcd_num = int(bin_str_out[(i * 4):(i + 1) * 4][::-1], 2)
        if bcd_num > 9:
            dec_num = -dec_num
        else:
            dec_num = dec_num + (bcd_num * pow(10, i))
    return dec_num


def validate_value_class(class_str):
    if class_str.upper() in ['FLOAT64', 'DOUBLE', 'FLOAT', 'LREAL', 'UNIXTIMEF64']:
        return 'FLOAT64'
    if class_str.upper() in ['FLOAT32', 'SINGLE', 'REAL', 'UNIXTIMEF32']:
        return 'FLOAT32'
    if class_str.upper() in ['UINT64']:
        return 'UINT64'
    if class_str.upper() in ['INT64', 'UNIXTIMEI64']:
        return 'INT64'
    if class_str.upper() in ['INT32']:
        return 'INT32'
    if class_str.upper() in ['UINT32', 'DWORD', 'UNIXTIMEI32']:
        return 'UINT32'
    if class_str.upper() in ['INT16', 'INT']:
        return 'INT16'
    if class_str.upper() in ['UINT', 'UINT16', 'WORD']:
        return 'UINT16'
    if class_str.upper() in ['INT8']:
        return 'INT8'
    if class_str.upper() in ['UINT8', 'BYTE']:
        return 'UINT8'
    if class_str.upper() in ['BOOL', 'BOOLEAN']:
        return 'BOOLEAN'
    else:
        return 'FLOAT64'


def _cast(value, class_str):
    if class_str.upper() in ['FLOAT64', 'DOUBLE', 'FLOAT', 'LREAL', 'FLOAT32', 'SINGLE', 'REAL', 'UNIXTIMEF32',
                             'UNIXTIMEF64']:
        return float(value)
    if class_str.upper() in ['INT32', 'UINT32', 'DWORD', 'INT16', 'INT', 'UINT', 'UINT16', 'WORD', 'INT8', 'UINT8',
                             'BYTE']:
        return int(value)
    if class_str.upper() in ['BOOL', 'BOOLEAN']:
        return value.lower() == 'true'
    else:
        return value


def datetime_now():
    return now()


def timestamp_to_datetime(timestamp, tz=UTC):
    return datetime.fromtimestamp(timestamp,tz)


def blow_up_data(data,timevalues,mean_value_period,no_mean_value = True):
    out_data = np.zeros(len(timevalues))
    # i                            # time data index
    ii = 0  # source data index
    # calculate mean values
    last_value = None
    max_ii = len(data) - 1
    for i in range(len(timevalues)):  # iter over time values

        if ii >= max_ii + 1:
            # if not more data in data source break
            if last_value is not None:
                out_data[i] = last_value
                continue
        # init mean value vars
        tmp = 0.0  # sum
        tmp_i = 0.0  # count

        if data[ii][0] < timevalues[i]:
            if ii == max_ii:
                last_value = data[ii][1]
            else:
                # skip elements that are befor current time step
                while data[ii][0] < timevalues[i] and ii < max_ii:
                    last_value = data[ii][1]
                    ii += 1

        if ii >= max_ii:
            if last_value is not None:
                out_data[i] = last_value
                continue
        # calc mean value
        if timevalues[i] <= data[ii][0] < timevalues[i] + mean_value_period:
            # there is data in time range
            while timevalues[i] <= data[ii][0] < timevalues[i] + mean_value_period and ii < max_ii:
                # calculate mean value
                if no_mean_value:
                    tmp = data[ii][1]
                    tmp_i = 1
                else:
                    tmp += data[ii][1]
                    tmp_i += 1

                last_value = data[ii][1]
                ii += 1
            # calc and store mean value
            if tmp_i > 0:
                out_data[i] = tmp / tmp_i
            else:
                out_data[i] = data[ii][1]
                last_value = data[ii][1]
        else:
            # there is no data in time range, keep last value, not mean value
            if last_value is not None:
                out_data[i] = last_value
    return np.asarray(out_data)


def min_pass(my_marks, my_pass, compare='lte'):
    min_value = None
    for x in my_marks:
        if x >= my_pass and compare == 'lte':
            min_value = x
            break
        elif x > my_pass and compare == 'lt':
            min_value = x
            break
    if min_value is not None:
        for x in my_marks:
            if min_value > x >= my_pass and compare == 'lte':
                min_value = x
            elif min_value > x > my_pass and compare == 'lt':
                min_value = x
    return min_value


def max_pass(my_marks, my_pass, compare='gte'):
    max_value = None
    for x in my_marks:
        if x <= my_pass and compare == 'gte':
            max_value = x
            break
        elif x < my_pass and compare == 'gt':
            max_value = x
            break
    if max_value is not None:
        for x in my_marks:
            if max_value < x <= my_pass and compare == 'gte':
                max_value = x
            elif max_value < x < my_pass and compare == 'gt':
                max_value = x
    return max_value
