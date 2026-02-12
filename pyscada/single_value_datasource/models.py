# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import time

from django.core.cache import cache
from django.db import models
from django.utils.timezone import now

from pyscada.models import DataSource, Variable
from pyscada.utils import timestamp_to_datetime

logger = logging.getLogger(__name__)


class DjangoSingleValue(models.Model):
    datasource = models.OneToOneField(DataSource, on_delete=models.CASCADE)

    def __str__(self):
        return f"Django single Value Datasource"

    def last_datapoint(self, variable=None, use_date_saved=False, **kwargs):
        """returns the last data for a given Variable in the cache and checks for stale
        data

        Args:
            variable_id: Primary Key of the Variable for which the data is stored
            new_data: in the form [[timestamp, value, (date_saved)], ...]
            date_saved (optional): date when the data was saved

        Returns:
            last element
        """
        if variable is None:
            logger.info(
                "No variable defined for DjangoCache last_datapoint function"
            )
            return None
        recorded_data = variable.singlevaluerecordeddata
        if recorded_data is None:
            return None
        data = [recorded_data.timestamp, recorded_data.value]
        
        if data is None:
            return None

        return data[0:2]

    def query_datapoints(
        self,
        variable_ids=[],
        time_min=0,
        time_max=None,
        query_first_value=False,
        time_min_excluded=False,
        time_max_excluded=False,
        **kwargs,
    ):
        """returns all data for a list of Variables in the cache in a given periode

        Args:
            variable_ids: Primary Key of the Variable for which the data is stored
            time_min (optional):
            time_min (optional):
            query_first_value (optional):
            time_min_excluded (optional):
            time_max_excluded (optional):


        Returns:
            datapoints
        """
        if time_max is None:
            time_max = time.time()

        variable_ids = self.datasource.datasource_check(
            items=variable_ids, items_as_id=True, ids_model=Variable
        )
        output = {}
        output["timestamp"] = 0
        output["date_saved_max"] = 0

        for variable_id in variable_ids:
            data = SingleValueRecordedData.objects.filter(variable_id=variable_id).last()
            
            if data is None:
                continue
            timestamp = data.timestamp
            value = data.value
            date_saved = data.date_saved.timestamp()

            if timestamp > time_max or (time_max_excluded and timestamp >= time_max):
                    continue

            if query_first_value:
                # short cut
                output[variable_id] = [[timestamp, value],]
                output["timestamp"] = max(output["timestamp"], timestamp)
                output["date_saved_max"] = max(output["date_saved_max"], date_saved)
                continue
            
            if timestamp < time_min or (time_min_excluded and timestamp <= time_min):
                continue
                
            output[variable_id] = [[timestamp, value],]
            output["timestamp"] = max(output["timestamp"], timestamp)
            output["date_saved_max"] = max(output["date_saved_max"], date_saved)
                
        return output

    def write_datapoints(self, items=[], date_saved=None, **kwargs):
        """
        Args:
            datapoints:  { variable_id: [[timestamp, value, date_saved]] } with
                timestamp in s and date_saved as datetime, timestamp in s or None
            date_saved (datetime, optional): time when the data was saved. Defaults to
                now()

        Returns:
            None
        """
        items = self.datasource.datasource_check(items)
        date_saved = date_saved if date_saved is not None else now()
        for item in items:
            logger.debug(f"{item} has {len(item.cached_values_to_write)} to write.")
            if not hasattr(item, "date_saved") or item.date_saved is None:
                item.date_saved = date_saved
            
            recorded_data = None
            if hasattr(recorded_data, "singlevaluerecordeddata"):
                recorded_data = item.singlevaluerecordeddata
            
            if recorded_data is None:
                recorded_data = SingleValueRecordedData(variable=item)
                
            if recorded_data.update_data(
                new_data=item.cached_values_to_write,
                date_saved=item.date_saved,
                ):
                recorded_data.save()
            
            item.date_saved = None

    def write_raw_datapoints(self, datapoints: dict, date_saved=None):
        """writes raw datapoints to the database in the form

        Args:
            datapoints:  { variable_id: [[timestamp, value, date_saved]] } with
                timestamp in s and date_saved as datetime, timestamp in s or None
            date_saved (datetime, optional): time when the data was saved. Defaults to
                now()

        Returns:
            None
        """
        for variable_id in datapoints.keys():
            for datapoint in datapoints[variable_id]:
                if len(datapoint) == 2:
                    if date_saved is None:
                        datapoint.append(now())
                    else:
                        datapoint.append(date_saved)

                elif len(datapoint) == 3:
                    if datapoint[2] is None:
                        if date_saved is None:
                            datapoint[2] = now()
                        else:
                            datapoint[2] = date_saved

                    elif type(datapoint[2]) is int or type(datapoint[2]) is float:
                        datapoint[2] = timestamp_to_datetime(datapoint[2])

                recorded_data = SingleValueRecordedData.objects.filter(variable_id=variable_id).last()
                if recorded_data is None:
                    recorded_data = SingleValueRecordedData(variable_id=variable_id)
                    
                if recorded_data.update_data(
                    new_data=[datapoint[0:2]],
                    date_saved=datapoint[2],
                    ):
                    recorded_data.save()


class SingleValueRecordedData(models.Model):
    variable = models.OneToOneField(Variable, null=True, on_delete=models.SET_NULL)
    date_saved = models.DateTimeField(db_index=True)
    value_boolean = models.BooleanField(default=False, blank=True)  # boolean
    value_int16 = models.SmallIntegerField(null=True, blank=True)  # int16, uint8, int8
    value_int32 = models.IntegerField(
        null=True, blank=True
    )  # uint8, int16, uint16, int32
    value_int64 = models.BigIntegerField(null=True, blank=True)  # uint32, int64, int48
    value_float64 = models.FloatField(null=True, blank=True)  # float64, float48
    timestamp = models.FloatField(db_index=True)
    
    
    @property
    def value(self):
        """
        return the stored value
        """
        if self.variable is None:
            return None

        if self.variable.value_class.upper() in [
            "FLOAT",
            "FLOAT64",
            "DOUBLE",
            "FLOAT32",
            "SINGLE",
            "REAL",
            "FLOAT48",
        ]:
            return self.value_float64
        elif self.variable.scaling and not self.variable.value_class.upper() in ["BOOL", "BOOLEAN"]:
            return self.value_float64
        elif self.variable.value_class.upper() in ["UINT64"]:
            # moving the int64 range [2**63, 2**63 - 1] stored as a django
            # BigIntegerField to the int64 [0, 2**64 - 1]
            value = self.value_int64
            if value is None:
                return value
            return value + 2**63
        elif self.variable.value_class.upper() in ["INT64", "UINT32", "DWORD", "INT48"]:
            return self.value_int64
        elif self.variable.value_class.upper() in ["WORD", "UINT", "UINT16", "INT32"]:
            return self.value_int32
        elif self.variable.value_class.upper() in ["INT16", "INT8", "UINT8"]:
            return self.value_int16
        elif self.variable.value_class.upper() in ["BOOL", "BOOLEAN"]:
            return self.value_boolean
        else:
            logger.warning(
                f"The {self.variable.value_class.upper()} variable value class is not defined in RecordedData value function. Default reading value as float."  # noqa: E501
            )
            return self.value_float64
        
        
    @value.setter
    def value(self, value):
        if self.variable.value_class.upper() in [
                "FLOAT",
                "FLOAT64",
                "DOUBLE",
                "FLOAT32",
                "SINGLE",
                "REAL",
                "FLOAT48",
            ]:
            self.value_float64 = float(value)
        elif self.variable.scaling and not self.variable.value_class.upper() in ["BOOL", "BOOLEAN"]:
                self.value_float64 = float(value)
        elif self.variable.value_class.upper() in ["UINT64"]:
            # moving the uint64 range [0, 2**64 - 1] to the int64
            # [-2**63, 2**63 - 1] to be stored as a django BigIntegerField
            self.value_int64 = int(value) - 2**63
            # See https://docs.djangoproject.com/en/stable/ref/models/fields/#bigintegerfield # noqa: E501
            if (
                self.value_int64 < -9223372036854775808
                or self.value_int64 > 9223372036854775807
            ):
                raise ValueError(
                    f"Saving value to RecordedData for {self.variable} with value class {self.variable.value_class.upper()} should be in the interval [0:18446744073709551615], it is {self.value_int64 + 2**63}"  # noqa: E501
                )
        elif self.variable.value_class.upper() in [
            "INT64",
            "UINT32",
            "DWORD",
            "INT48",
        ]:
            self.value_int64 = int(value)
            # See https://docs.djangoproject.com/en/stable/ref/models/fields/#bigintegerfield # noqa: E501
            if (
                self.value_int64 < -9223372036854775808
                or self.value_int64 > 9223372036854775807
            ):
                raise ValueError(
                    f"Saving value to RecordedData for {self.variable} with value class {self.variable.value_class.upper()} should be in the interval [-9223372036854775808:9223372036854775807], it is {self.value_int64}"  # noqa: E501
                )
        elif self.variable.value_class.upper() in [
            "WORD",
            "UINT",
            "UINT16",
            "INT32",
        ]:
            self.value_int32 = int(value)
            # See https://docs.djangoproject.com/en/stable/ref/models/fields/#integerfield # noqa: E501
            if (
                self.value_int32 < -2147483648
                or self.value_int32 > 2147483647
            ):
                raise ValueError(
                    f"Saving value to RecordedData for {self.variable} with value class {self.variable.value_class.upper()} should be in the interval [-2147483648:2147483647], it is {self.value_int32}"  # noqa: E501
                )
        elif self.variable.value_class.upper() in [
            "INT16",
            "INT8",
            "UINT8",
            "INT",
        ]:
            self.value_int16 = int(value)
            # See https://docs.djangoproject.com/en/stable/ref/models/fields/#smallintegerfield # noqa: E501
            if self.value_int16 < -32768 or self.value_int16 > 32767:
                raise ValueError(
                    f"Saving value to RecordedData for {self.variable} with value class {self.variable.value_class.upper()} should be in the interval [-32768:32767], it is {self.value_int16}"  # noqa: E501
                )
        elif self.variable.value_class.upper() in ["BOOL", "BOOLEAN"]:
            self.value_boolean = bool(value)
        else:
            logger.warning(
                f"The {self.variable.value_class.upper()} variable value class is not defined in RecordedData __init__ function. Default storing value as float."  # noqa: E501
            )
            self.value_float64 = float(value)
    
    
    def update_data(self, new_data:list, date_saved)-> bool:
        """will take a list of [timestamp, value] pairs an write the latest to the DB
        
        """
        data_timestamp_max = 0
        last_value = None
        for timestamp, value in new_data:
            if self.timestamp is not None and timestamp < self.timestamp:
                continue
            if timestamp < data_timestamp_max:
                continue
            data_timestamp_max = timestamp
            last_value = value
        if last_value is None:
            return False
        
        self.value = last_value
        self.timestamp = timestamp
        self.date_saved = date_saved
        return True
        
            
            
            
            
    
        
        
        
        
