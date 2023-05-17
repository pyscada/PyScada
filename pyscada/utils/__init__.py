#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re
from datetime import datetime
from pytz import UTC
import numpy as np
from django.utils.timezone import now
from django.template.loader import get_template
from django.contrib.auth.models import Group
import logging
logger = logging.getLogger(__name__)


def _get_objects_for_html(list_to_append=None, obj=None, exclude_model_names=None):
    if obj is not None:
        if exclude_model_names is None:
            exclude_model_names = list()
        if list_to_append is None:
            list_to_append = set()

        if obj not in list_to_append:
            list_to_append.update([obj])
        # ForeignKey and OneToOne
        for field in obj._meta.local_fields:
            if (type(field).many_to_one or type(field).one_to_one) and getattr(obj, field.name) is not None and \
                    field.name not in exclude_model_names:
                if hasattr(field.related_model, '_get_objects_for_html'):
                    list_to_append.update(getattr(obj, field.name)._get_objects_for_html(list_to_append))
                else:
                    list_to_append.update(_get_objects_for_html(list_to_append, getattr(obj, field.name)))
        # ManyToMany
        for fields in obj._meta.local_many_to_many:
            for field in getattr(obj, fields.name).all():
                if field not in exclude_model_names:
                    if hasattr(field, '_get_objects_for_html'):
                        list_to_append.update(field._get_objects_for_html(list_to_append))
                    else:
                        list_to_append.update(_get_objects_for_html(list_to_append, field))
        # Related OneToOne
        for field in obj._meta.related_objects:
            if field.one_to_one and hasattr(obj, field.name) and field.name not in exclude_model_names and getattr(obj, field.name) not in list_to_append:
                name = field.field.name
                field = getattr(obj, field.name)
                if hasattr(field, '_get_objects_for_html'):
                    list_to_append.update(field._get_objects_for_html(list_to_append, exclude_model_names=[name]))
                else:
                    list_to_append.update(_get_objects_for_html(list_to_append, field, exclude_model_names=[name]))

    return list_to_append


def get_group_display_permission_list(items, groups):
    """
    @params:
        items: QuerySet of items to filter
        groups: QuerySet of groups to filter by
    @return:
        QuerySet of items filtered
    """
    if len(groups) == 0:
        result = items.filter(
            groupdisplaypermission__group_display_permission__hmi_group__isnull=True,
            groupdisplaypermission__type=0,
        ).distinct()
        if items.first() is not None and items.first().groupdisplaypermission.model.objects.filter(type=1, group_display_permission__hmi_group=None).exists():
            result = result | items.exclude(
                groupdisplaypermission__group_display_permission__hmi_group__isnull=True,
                groupdisplaypermission__type=1
            ).distinct()
    else:
        result = items.filter(
            groupdisplaypermission__group_display_permission__hmi_group__in=groups,
            groupdisplaypermission__type=0,
        ).distinct()
        if items.first() is not None and items.first().groupdisplaypermission.model.objects.filter(type=1, group_display_permission__hmi_group__in=groups).exists():
            result = result | items.exclude(
                groupdisplaypermission__group_display_permission__hmi_group__in=groups,
                groupdisplaypermission__type=1
            ).distinct()
    return result


def gen_hiddenConfigHtml(obj, custom_fields=None):
    """
    Get an object and return an html with a hidden div containing the object
    config

    :param obj: an object from a model
    :param custom_fields: list of fields to add to the result

    :return: the html of the config of the object
    """
    fields = list()
    for field in obj._meta.local_many_to_many:
        # For ManyToManyField
        l = ""
        for o in field.value_from_object(obj):
            l += str(o.pk) + ","
        fields.append(dict(
            name=field.name,
            value=l,
        ))
    for field in obj._meta.local_fields:
        value = field.value_from_object(obj)
        if type(value) == datetime:
            value = value.timestamp()
        fields.append(dict(
            name=field.name,
            value=value,
        ))
    if type(custom_fields) == list:
        for field in custom_fields:
            if type(field) == dict and 'name' in field and 'value' in field:
                fields.append(dict(
                    name=field['name'],
                    value=field['value'],
                ))

    return get_template('modelProperties.html').render(dict(
        modelName=obj._meta.model_name,
        fields=fields,
    ))


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
    if isinstance(values, int):
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


def min_pass(my_marks, my_pass, compare='gte'):
    min_value = None
    for x in my_marks:
        if x >= my_pass and compare == 'gte':
            min_value = x
            break
        elif x > my_pass and compare == 'gt':
            min_value = x
            break
    if min_value is not None:
        for x in my_marks:
            if min_value > x >= my_pass and compare == 'gte':
                min_value = x
            elif min_value > x > my_pass and compare == 'gt':
                min_value = x
    return min_value


def max_pass(my_marks, my_pass, compare='lte'):
    max_value = None
    for x in my_marks:
        if x <= my_pass and compare == 'lte':
            max_value = x
            break
        elif x < my_pass and compare == 'lt':
            max_value = x
            break
    if max_value is not None:
        for x in my_marks:
            if max_value < x <= my_pass and compare == 'lte':
                max_value = x
            elif max_value < x < my_pass and compare == 'lt':
                max_value = x
    return max_value


def set_bit(v, index, x):
    """Set the index:th bit of v to 1 if x is truthy, else to 0, and return the new value."""
    mask = 1 << index   # Compute mask, an integer with just bit 'index' set.
    v &= ~mask          # Clear the bit indicated by the mask (if x is False)
    if x:
        v |= mask         # If x was True, set the bit indicated by the mask.
    return v            # Return the result, we're done.
