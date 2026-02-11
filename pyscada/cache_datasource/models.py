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


class DjangoCache(models.Model):
    datasource = models.OneToOneField(DataSource, on_delete=models.CASCADE)
    data_lifetime = models.PositiveIntegerField(default=3600)

    def __str__(self):
        return f"Django Cache (data lifetime : {self.data_lifetime} seconds)"

    @staticmethod
    def now_ms() -> int:
        """returns a unixtimestamp in ms"""
        return int(now().timestamp() * 1000)

    @property
    def _data_lifetime_ms(self) -> int:
        """returns the lifetime of data in the cache in ms"""
        return self.data_lifetime * 1000

    def _make_key(self, variable_id: int) -> str:
        """returns the key to find the Variable data in the cache

        Args:
            variable_id: Primary Key of the Variable for which the data is stored

        Returns:
            cache key
        """
        return f"{self.pk}_{variable_id}"

    def _get_data(self, variable_id: int):
        """returns the data for a given Variable from the cache

        Args:
            variable_id: Primary Key of the Variable for which the data is stored

        Returns:
            cache data or None
        """
        return cache.get(self._make_key(variable_id))

    def _set_data(self, variable_id: int, data: list) -> bool:
        """stores the data for a given Variable in the cache

        Args:
            variable_id: Primary Key of the Variable for which the data is stored
            data: in the form [[timestamp, value, date_saved], ...]

        Returns:
            cache status
        """
        return cache.set(self._make_key(variable_id), data, timeout=self.data_lifetime)

    def _update_variable_data(self, variable_id: int, new_data=None, date_saved=None):
        """stores the data for a given Variable in the cache and checks for stale data

        Args:
            variable_id: Primary Key of the Variable for which the data is stored
            new_data: in the form [[timestamp, value, (date_saved)], ...]
            date_saved (optional): date when the data was saved

        Returns:
            cache status
        """
        data = self._get_data(variable_id=variable_id)
        if data is None:
            data = {}
        if new_data is None:
            new_data = []
        date_saved = date_saved if date_saved is not None else now()

        # check for old data
        for key in list(data.keys()):
            if key < (self.now_ms() - self._data_lifetime_ms):
                logger.error(
                    f"{key} smaler than {(self.now_ms() - self._data_lifetime_ms)}"
                )
                del data[key]

        for value in new_data:
            data[int(value[0] * 1000)] = [value[0], value[1], date_saved.timestamp()]

        return self._set_data(variable_id=variable_id, data=data)

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
        data = self._get_data(variable_id=variable.pk)

        if data is None:
            logger.debug(
                "No data"
            )
            return None
        last_element = None
        for timestamp_ms, item in data.items():
            timestamp = item[0]
            value = item[1]
            if last_element is None:
                last_element = [timestamp, value]
                continue

            if last_element[0] < timestamp:
                last_element = [timestamp, value]

        if last_element is None:
            return None

        return last_element

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
            data = self._get_data(variable_id=variable_id)
            if data is None:
                continue

            first_value = None
            for timestamp_ms, item in data.items():
                timestamp = item[0]
                value = item[1]
                date_saved = item[2]

                if timestamp > time_max:
                    continue
                if time_max_excluded and timestamp >= time_max:
                    continue
                if timestamp < time_min or (
                    time_min_excluded and timestamp <= time_min
                ):
                    if not query_first_value:
                        continue
                    if first_value is None:
                        first_value = [timestamp, value, date_saved]
                    elif first_value[0] < timestamp:
                        first_value = [timestamp, value, date_saved]
                    continue
                if variable_id not in output:
                    output[variable_id] = []
                output[variable_id].append([timestamp, value])
                output["timestamp"] = max(output["timestamp"], timestamp)
                output["date_saved_max"] = max(output["date_saved_max"], date_saved)

            if query_first_value and first_value is not None:
                if variable_id not in output:
                    output[variable_id] = []
                # prepend last value
                output[variable_id] = [first_value[0:2]] + output[variable_id]
                output["timestamp"] = max(output["timestamp"], first_value[0])
                output["date_saved_max"] = max(output["date_saved_max"], first_value[2])

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
            self._update_variable_data(
                variable_id=item.pk,
                new_data=item.cached_values_to_write,
                date_saved=item.date_saved,
            )
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

                self._update_variable_data(
                    variable_id=variable_id,
                    new_data=[[datapoint[0], datapoint[1]]],
                    date_saved=datapoint[2],
                )
