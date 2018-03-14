#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re
from datetime import datetime
from pytz import UTC
from django.utils.six import integer_types
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
    return datetime.now(UTC)

