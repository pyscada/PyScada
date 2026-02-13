# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import time

from django.core.exceptions import ValidationError
from django.db import models
from django.db.utils import IntegrityError
from django.utils.timezone import now

from pyscada.models import DataSource, Variable
from pyscada.utils import timestamp_to_datetime

logger = logging.getLogger(__name__)


class RecordedDataManager(models.Manager):
    def create_data_element_from_variable(
        self, variable, value, timestamp, date_saved=None, **kwargs
    ):
        if value is None:
            return None

        if date_saved is None:
            date_saved = (
                variable.date_saved if hasattr(variable, "date_saved") else now()
            )

        return RecordedData(
            timestamp=timestamp,
            variable=variable,
            value=value,
            date_saved=date_saved,
        )

    def last_element(
        self,
        time_min=0,
        time_max=None,
        use_date_saved=True,
        timeout=None,
        time_min_excluded=False,
        time_max_excluded=False,
        **kwargs,
    ):

        if time_max is None:
            time_max = time.time()

        # if True, remove the tim_min point from the range
        time_min_offset = 0
        if time_min_excluded:
            time_min_offset = 2097152

        # if True, remove the tim_max point from the range
        time_max_offset = 0
        if time_max_excluded:
            time_max_offset = 2097152

        if use_date_saved:
            result = (
                super()
                .get_queryset()
                .filter(
                    date_saved__range=(
                        timestamp_to_datetime(time_min),
                        timestamp_to_datetime(time_max),
                    ),
                    **kwargs,
                )
            )
            if result is not None and len(result) > 0:
                if time_min_excluded and result[0].date_saved == timestamp_to_datetime(
                    time_min
                ):
                    result = result[1:]
                if time_max_excluded and result[
                    len(result) - 1
                ].date_saved == timestamp_to_datetime(time_max):
                    result = result[: len(result) - 1]
            return result.last()
        else:
            return (
                super()
                .get_queryset()
                .filter(
                    id__range=(
                        time_min * 2097152 * 1000 + time_min_offset,
                        time_max * 2097152 * 1000 + 2097151 - time_max_offset,
                    ),
                    **kwargs,
                )
                .last()
            )

    def db_data(
        self,
        variable_ids,
        time_min,
        time_max,
        query_first_value=False,
        **kwargs,
    ):
        """

        :return:
        """

        if kwargs.get("time_min_excluded", False):
            time_min = time_min + 0.001
        if kwargs.get("time_max_excluded", False):
            time_max = time_max - 0.001

        variable_ids = [int(pk) for pk in variable_ids]
        tmp = list(
            super()
            .get_queryset()
            .filter(
                id__range=(
                    time_min * 2097152 * 1000,
                    time_max * 2097152 * 1000 + 2097151,
                ),
                # date_saved__range=(
                #    timestamp_to_datetime(
                #        time_min - 3660 if query_first_value else time_min
                #    ),
                #    timestamp_to_datetime(time_max),
                # ),
                variable_id__in=variable_ids,
            )
            .values_list(
                "variable_id",
                "pk",
                "value_float64",
                "value_int64",
                "value_int32",
                "value_int16",
                "value_boolean",
                "date_saved",
            )
        )

        values = dict()
        times = dict()
        date_saved_max = 0
        tmp_time_max = 0
        tmp_time_min = time_max

        def get_rd_value(rd_resp):
            # return the value from a RecordedData Response
            if rd_resp[2] is not None:  # float64
                return rd_resp[2]  # time, value
            elif rd_resp[3] is not None:  # int64
                return rd_resp[3]  # time, value
            elif rd_resp[4] is not None:  # int32
                return rd_resp[4]  # time, value
            elif rd_resp[5] is not None:  # int16
                return rd_resp[5]  # time, value
            elif rd_resp[6] is not None:  # boolean
                return rd_resp[6]  # time, value
            else:
                return 0

        for item in tmp:
            if item[0] not in variable_ids:
                continue
            if not item[0] in values:
                values[item[0]] = []
                times[item[0]] = {"time_min": time_max, "time_max": 0}
            tmp_time = float(item[1] - item[0]) / (
                2097152.0 * 1000
            )  # calc the timestamp in seconds
            if item[7] is None:
                continue
            date_saved_max = max(
                date_saved_max,
                time.mktime(item[7].utctimetuple()) + item[7].microsecond / 1e6,
            )
            tmp_time_max = max(tmp_time, tmp_time_max)
            tmp_time_min = min(tmp_time, tmp_time_min)
            values[item[0]].append([tmp_time, get_rd_value(item)])
            if tmp_time < times[item[0]]["time_min"]:
                times[item[0]]["time_min"] = tmp_time
            if tmp_time > times[item[0]]["time_max"]:
                times[item[0]]["time_max"] = tmp_time

        if query_first_value:
            for pk in variable_ids:
                if pk not in values:
                    values[pk] = []
                time_max_last_value = time_max
                time_max_excluded = False
                if pk in times:
                    time_max_last_value = times[pk]["time_min"]
                    time_max_excluded = True
                last_element = self.last_element(
                    use_date_saved=False,
                    time_min=0,
                    time_max=time_max_last_value,
                    time_max_excluded=time_max_excluded,
                    variable_id=pk,
                )
                if last_element is not None and last_element.date_saved is not None:
                    tmp_time = last_element.time_value()
                    values[pk].insert(
                        0,
                        [
                            tmp_time,
                            last_element.value(),
                        ],
                    )
                    date_saved_max = max(
                        date_saved_max,
                        time.mktime(last_element.date_saved.utctimetuple())
                        + last_element.date_saved.microsecond / 1e6,
                    )
                    tmp_time_max = max(tmp_time, tmp_time_max)

        # values["timestamp"] = max(tmp_time_max, time_min)
        values["timestamp"] = tmp_time_max
        values["date_saved_max"] = date_saved_max

        return values


class DjangoDatabase(models.Model):
    datasource = models.OneToOneField(DataSource, on_delete=models.CASCADE)
    data_model_app_name = models.CharField(
        max_length=50,
    )
    data_model_name = models.CharField(
        max_length=50,
    )

    def __str__(self):
        return f"Django database ({self.data_model_app_name}.{self.data_model_name})"

    def _import_model(self):
        class_name = self.data_model_name
        class_path = self.data_model_app_name + ".models"
        try:
            mod = __import__(class_path, fromlist=[class_name])
            content_class = getattr(mod, class_name)
            if isinstance(content_class, models.base.ModelBase):
                return content_class
        except ModuleNotFoundError:
            logger.info(
                f"{class_name} of {class_path} not found. A module is not installed ?"
            )
        except:  # noqa: E722
            logger.error(f"{class_path} unhandled exception", exc_info=True)
        return None

    def last_value(self, **kwargs):
        logger.info(
            "the use of 'last_value' method is deprecated use 'last_datapoint' instead"
        )
        return self.last_datapoint(**kwargs)

    def last_datapoint(self, variable=None, use_date_saved=False, **kwargs):
        if variable is None:
            logger.info(
                "No variable defined for DjangoDatabase last_datapoint function"
            )
            return None
        data_model = self._import_model()
        last_element = data_model.objects.last_element(
            use_date_saved=use_date_saved, variable_id=variable.pk, **kwargs
        )
        if last_element is not None:
            return [last_element.time_value(), last_element.value()]
        else:
            return None

    def read_multiple(self, **kwargs):
        logger.info(
            "the use of 'read_multiple' method is deprecated use 'query_datapoints' instead"  # noqa: E501
        )
        return self.query_datapoints(**kwargs)

    def query_datapoints(
        self,
        variable_ids=[],
        time_min=0,
        time_max=None,
        query_first_value=False,
        **kwargs,
    ):
        if time_max is None:
            time_max = time.time()

        variable_ids = self.datasource.datasource_check(
            items=variable_ids, items_as_id=True, ids_model=Variable
        )
        return self._import_model().objects.db_data(
            variable_ids=variable_ids,
            time_min=time_min,
            time_max=time_max,
            query_first_value=query_first_value,
            **kwargs,
        )

    def write_multiple(self, **kwargs):
        logger.info(
            "the use of 'write_multiple' method is deprecated use 'write_datapoints' instead"  # noqa: E501
        )
        return self.write_datapoints(**kwargs)

    def write_datapoints(self, items=[], date_saved=None, batch_size=1000, **kwargs):
        """
        Args:
            datapoints:  { variable_id: [[timestamp, value, date_saved]] } with
                timestamp in s and date_saved as datetime, timestamp in s or None
            date_saved (datetime, optional): time when the data was saved. Defaults to
                now()
            batch_size (int): Number of values to safe in bulk_create at once. Defauls
                to 1000

        Returns:
            None
        """
        data_model = self._import_model()
        items = self.datasource.datasource_check(items)
        recorded_datas = []
        date_saved = date_saved if date_saved is not None else now()
        for item in items:
            logger.debug(f"{item} has {len(item.cached_values_to_write)} to write.")
            if len(item.cached_values_to_write):
                for cached_value in item.cached_values_to_write:
                    # add date saved if not exist in variable object, if date_saved is
                    # in kwargs it will be used instead of the variable.date_saved
                    # (see the create_data_element_from_variable function)
                    if not hasattr(item, "date_saved") or item.date_saved is None:
                        item.date_saved = date_saved
                    # create the recorded data object
                    rc = data_model.objects.create_data_element_from_variable(
                        item, cached_value[1], cached_value[0], **kwargs
                    )
                    # append the object to the elements to save
                    if rc is not None:
                        recorded_datas.append(rc)

        try:
            data_model.objects.bulk_create(recorded_datas, **kwargs)
        except IntegrityError:
            logger.debug(
                f'{data_model._meta.object_name} objects already exists, retrying ignoring conflicts for : {", ".join(str(i.id) + " " + str(i.variable.id) for i in recorded_datas)}'  # noqa: E501
            )
            data_model.objects.bulk_create(
                recorded_datas, ignore_conflicts=True, **kwargs
            )
        for item in items:
            item.date_saved = None
            item.erase_cache()

    def write_raw_datapoints(self, datapoints: dict, date_saved=None, batch_size=1000):
        """writes raw datapoints to the database in the form

        Args:
            datapoints:  { variable_id: [[timestamp, value, date_saved]] } with
                timestamp in s and date_saved as datetime, timestamp in s or None
            date_saved (datetime, optional): time when the data was saved. Defaults to
                now()
            batch_size (int): Number of values to safe in bulk_create at once. Defauls
                to 1000

        Returns:
            None
        """
        data_model = self._import_model()
        recorded_datas = []
        for variable_id in datapoints.keys():
            variable = Variable.objects.filter(pk=variable_id).first()
            for datapoint in datapoints[variable_id]:
                if len(datapoint)==2:
                    if date_saved is None:
                        datapoint.append(now())
                    else:
                        datapoint.append(date_saved)

                elif len(datapoint)==3:
                    if datapoint[2] is None:
                        if date_saved is None:
                            datapoint[2]=now()
                        else:
                            datapoint[2]=date_saved

                    elif (type(datapoint[2]) is int or type(datapoint[2]) is float):
                        datapoint[2]=timestamp_to_datetime(datapoint[2])

                #datapoint[0] *= 1000 # convert timestamp from s to ms

                rc = data_model.objects.create_data_element_from_variable(
                    variable=variable,
                    value=datapoint[1],
                    timestamp=datapoint[0],
                    date_saved=datapoint[2],
                )

                if rc is not None:
                    recorded_datas.append(rc)

        try:
            data_model.objects.bulk_create(recorded_datas, batch_size=batch_size)
        except IntegrityError:
            logger.debug(
                f'{data_model._meta.object_name} objects already exists, retrying ignoring conflicts for : {", ".join(str(i.id) + " " + str(i.variable.id) for i in recorded_datas)}'  # noqa: E501
            )
            data_model.objects.bulk_create(
                recorded_datas, ignore_conflicts=True, batch_size=batch_size
            )

    class Meta:
        db_table = "pyscada_djangodatabase"


class RecordedDataOld(models.Model):
    """
    Big Int first 42 bits are used for the unixtime in ms, unsigned because we only
    store time values that are later than 1970, rest 21 bits are used for the
    variable id to have a uniqe primary key
    63 bit 111111111111111111111111111111111111111111111111111111111111111
    42 bit 111111111111111111111111111111111111111111000000000000000000000
    21 bit 										    1000000000000000000000
    """

    id = models.BigIntegerField(primary_key=True)
    value_boolean = models.BooleanField(default=False, blank=True)  # boolean
    value_int16 = models.SmallIntegerField(null=True, blank=True)  # int16, uint8, int8
    value_int32 = models.IntegerField(
        null=True, blank=True
    )  # uint8, int16, uint16, int32
    value_int64 = models.BigIntegerField(null=True, blank=True)  # uint32, int64
    value_float64 = models.FloatField(null=True, blank=True)  # float64
    variable = models.ForeignKey(Variable, null=True, on_delete=models.SET_NULL)

    def __init__(self, *args, **kwargs):
        if "timestamp" in kwargs:
            timestamp = kwargs.pop("timestamp")
        else:
            timestamp = time.time()
        if "variable_id" in kwargs:
            variable_id = kwargs["variable_id"]
        elif "variable" in kwargs:
            variable_id = kwargs["variable"].pk
        else:
            variable_id = None

        if variable_id is not None and "id" not in kwargs:
            kwargs["id"] = int(int(int(timestamp * 1000) * 2097152) + variable_id)
        if "variable" in kwargs and "value" in kwargs:
            if kwargs["variable"].value_class.upper() in [
                "FLOAT",
                "FLOAT64",
                "DOUBLE",
                "FLOAT32",
                "SINGLE",
                "REAL",
            ]:
                kwargs["value_float64"] = float(kwargs.pop("value"))
            elif kwargs["variable"].scaling and not kwargs[
                "variable"
            ].value_class.upper() in ["BOOL", "BOOLEAN"]:
                kwargs["value_float64"] = float(kwargs.pop("value"))
            elif kwargs["variable"].value_class.upper() in ["INT64", "UINT32", "DWORD"]:
                kwargs["value_int64"] = int(kwargs.pop("value"))
                # See https://docs.djangoproject.com/en/stable/ref/models/fields/#bigintegerfield # noqa: E501
                if (
                    kwargs["value_int64"] < -9223372036854775808
                    or kwargs["value_int64"] > 9223372036854775807
                ):
                    raise ValueError(
                        f"Saving value to RecordedDataOld for {kwargs['variable']} with value class {kwargs['variable'].value_class.upper()} should be in the interval [-9223372036854775808:9223372036854775807], it is {kwargs['value_int64']}"  # noqa: E501
                    )
            elif kwargs["variable"].value_class.upper() in [
                "WORD",
                "UINT",
                "UINT16",
                "INT32",
            ]:
                kwargs["value_int32"] = int(kwargs.pop("value"))
                # See https://docs.djangoproject.com/en/stable/ref/models/fields/#integerfield # noqa: E501
                if (
                    kwargs["value_int32"] < -2147483648
                    or kwargs["value_int32"] > 2147483647
                ):
                    raise ValueError(
                        f"Saving value to RecordedDataOld for {kwargs['variable']} with value class {kwargs['variable'].value_class.upper()} should be in the interval [-2147483648:2147483647], it is {kwargs['value_int32']}"  # noqa: E501
                    )
            elif kwargs["variable"].value_class.upper() in [
                "INT16",
                "INT8",
                "UINT8",
                "INT",
            ]:
                kwargs["value_int16"] = int(kwargs.pop("value"))
                # See https://docs.djangoproject.com/en/stable/ref/models/fields/#smallintegerfield # noqa: E501
                if kwargs["value_int16"] < -32768 or kwargs["value_int16"] > 32767:
                    raise ValueError(
                        f"Saving value to RecordedDataOld for {kwargs['variable']} with value class {kwargs['variable'].value_class.upper()} should be in the interval [-32768:32767], it is {kwargs['value_int16']}"  # noqa: E501
                    )
            elif kwargs["variable"].value_class.upper() in ["BOOL", "BOOLEAN"]:
                kwargs["value_boolean"] = bool(kwargs.pop("value"))

        # call the django model __init__
        super(RecordedDataOld, self).__init__(*args, **kwargs)
        self.timestamp = self.time_value()

    def calculate_pk(self, timestamp=None):
        """
        calculate the primary key from the timestamp in seconds
        """
        if timestamp is None:
            timestamp = time.time()
        self.pk = int(int(int(timestamp * 1000) * 2097152) + self.variable.pk)

    def __str__(self):
        return str(self.value())

    def time_value(self):
        """
        return the timestamp in seconds calculated from the id
        """
        return (self.pk - self.variable.pk) / 2097152 / 1000.0  # value in seconds

    def value(self, value_class=None):
        """
        return the stored value
        """
        if value_class is None:
            value_class = self.variable.value_class

        if value_class.upper() in [
            "FLOAT",
            "FLOAT64",
            "DOUBLE",
            "FLOAT32",
            "SINGLE",
            "REAL",
        ]:
            return self.value_float64
        elif self.variable.scaling and not value_class.upper() in ["BOOL", "BOOLEAN"]:
            return self.value_float64
        elif value_class.upper() in ["INT64", "UINT32", "DWORD"]:
            return self.value_int64
        elif value_class.upper() in ["WORD", "UINT", "UINT16", "INT32"]:
            return self.value_int32
        elif value_class.upper() in ["INT16", "INT8", "UINT8"]:
            return self.value_int16
        elif value_class.upper() in ["BOOL", "BOOLEAN"]:
            return self.value_boolean
        else:
            return None

    class Meta:
        db_table = "pyscada_recordeddataold"


class RecordedData(models.Model):
    """
    id: Big Int first 42 bits are used for the unix time in ms, unsigned because we only
    store values that are past 1970, the last 21 bits are used for the
    variable id to have a unique primary key
    63 bit 111111111111111111111111111111111111111111111111111111111111111
    42 bit 111111111111111111111111111111111111111111000000000000000000000
    21 bit 										    1000000000000000000000
    date_saved: datetime when the model instance is saved in the database
    (will be set in the save method)
    """

    id = models.BigIntegerField(primary_key=True)
    date_saved = models.DateTimeField(blank=True, null=True, db_index=True)
    value_boolean = models.BooleanField(default=False, blank=True)  # boolean
    value_int16 = models.SmallIntegerField(null=True, blank=True)  # int16, uint8, int8
    value_int32 = models.IntegerField(
        null=True, blank=True
    )  # uint8, int16, uint16, int32
    value_int64 = models.BigIntegerField(null=True, blank=True)  # uint32, int64, int48
    value_float64 = models.FloatField(null=True, blank=True)  # float64, float48
    variable = models.ForeignKey(Variable, null=True, on_delete=models.SET_NULL)

    objects = RecordedDataManager()

    def __init__(self, *args, **kwargs):

        timestamp = kwargs.get("timestamp", time.time_ns() / 1000000000)
        if "timestamp" in kwargs:
            kwargs.pop("timestamp")
        if "variable" in kwargs:
            variable_id = kwargs["variable"].pk
        elif "variable_id" in kwargs:
            variable_id = kwargs["variable_id"]
            try:
                kwargs["variable"] = Variable.objects.get(id=variable_id)
            except Variable.DoesNotExist:
                raise ValidationError(
                    f"Variable with id {variable_id} not found. Cannot save data."
                )
        else:
            variable_id = None

        if variable_id is not None and "id" not in kwargs:
            try:
                kwargs["id"] = int(
                    int(int(float(timestamp) * 1000) * 2097152) + variable_id
                )
            except (TypeError, ValueError) as e:
                raise ValidationError(
                    f"Cannot save data for variable {kwargs['variable']}, timestamp error : {e}"  # noqa: E501
                )
        if "variable" in kwargs and "value" in kwargs:
            if kwargs["variable"].value_class.upper() in [
                "FLOAT",
                "FLOAT64",
                "DOUBLE",
                "FLOAT32",
                "SINGLE",
                "REAL",
                "FLOAT48",
            ]:
                kwargs["value_float64"] = float(kwargs.pop("value"))
            elif kwargs["variable"].scaling and not kwargs[
                "variable"
            ].value_class.upper() in ["BOOL", "BOOLEAN"]:
                kwargs["value_float64"] = float(kwargs.pop("value"))
            elif kwargs["variable"].value_class.upper() in ["UINT64"]:
                # moving the uint64 range [0, 2**64 - 1] to the int64
                # [-2**63, 2**63 - 1] to be stored as a django BigIntegerField
                kwargs["value_int64"] = int(kwargs.pop("value")) - 2**63
                # See https://docs.djangoproject.com/en/stable/ref/models/fields/#bigintegerfield # noqa: E501
                if (
                    kwargs["value_int64"] < -9223372036854775808
                    or kwargs["value_int64"] > 9223372036854775807
                ):
                    raise ValueError(
                        f"Saving value to RecordedData for {kwargs['variable']} with value class {kwargs['variable'].value_class.upper()} should be in the interval [0:18446744073709551615], it is {kwargs['value_int64'] + 2**63}"  # noqa: E501
                    )
            elif kwargs["variable"].value_class.upper() in [
                "INT64",
                "UINT32",
                "DWORD",
                "INT48",
            ]:
                kwargs["value_int64"] = int(kwargs.pop("value"))
                # See https://docs.djangoproject.com/en/stable/ref/models/fields/#bigintegerfield # noqa: E501
                if (
                    kwargs["value_int64"] < -9223372036854775808
                    or kwargs["value_int64"] > 9223372036854775807
                ):
                    raise ValueError(
                        f"Saving value to RecordedData for {kwargs['variable']} with value class {kwargs['variable'].value_class.upper()} should be in the interval [-9223372036854775808:9223372036854775807], it is {kwargs['value_int64']}"  # noqa: E501
                    )
            elif kwargs["variable"].value_class.upper() in [
                "WORD",
                "UINT",
                "UINT16",
                "INT32",
            ]:
                kwargs["value_int32"] = int(kwargs.pop("value"))
                # See https://docs.djangoproject.com/en/stable/ref/models/fields/#integerfield # noqa: E501
                if (
                    kwargs["value_int32"] < -2147483648
                    or kwargs["value_int32"] > 2147483647
                ):
                    raise ValueError(
                        f"Saving value to RecordedData for {kwargs['variable']} with value class {kwargs['variable'].value_class.upper()} should be in the interval [-2147483648:2147483647], it is {kwargs['value_int32']}"  # noqa: E501
                    )
            elif kwargs["variable"].value_class.upper() in [
                "INT16",
                "INT8",
                "UINT8",
                "INT",
            ]:
                kwargs["value_int16"] = int(kwargs.pop("value"))
                # See https://docs.djangoproject.com/en/stable/ref/models/fields/#smallintegerfield # noqa: E501
                if kwargs["value_int16"] < -32768 or kwargs["value_int16"] > 32767:
                    raise ValueError(
                        f"Saving value to RecordedData for {kwargs['variable']} with value class {kwargs['variable'].value_class.upper()} should be in the interval [-32768:32767], it is {kwargs['value_int16']}"  # noqa: E501
                    )
            elif kwargs["variable"].value_class.upper() in ["BOOL", "BOOLEAN"]:
                kwargs["value_boolean"] = bool(kwargs.pop("value"))
            else:
                logger.warning(
                    f"The {kwargs['variable'].value_class.upper()} variable value class is not defined in RecordedData __init__ function. Default storing value as float."  # noqa: E501
                )
                kwargs["value_float64"] = float(kwargs.pop("value"))

        # call the django model __init__
        super(RecordedData, self).__init__(*args, **kwargs)
        if self.variable is not None:
            self.timestamp = self.time_value()
        elif self.date_saved is not None:
            self.timestamp = self.date_saved.timestamp()
        else:
            self.timestamp = time.time()

    def calculate_pk(self, timestamp=None):
        """
        calculate the primary key from the timestamp in seconds
        """
        if timestamp is None:
            timestamp = time.time()
        self.pk = int(int(int(timestamp * 1000) * 2097152) + self.variable.pk)

    def __str__(self):
        return str(self.value())

    def time_value(self):
        """
        return the timestamp in seconds calculated from the id
        """
        return (self.pk - self.variable.pk) / 2097152 / 1000.0  # value in seconds

    def value(self, value_class=None):
        """
        return the stored value
        """
        if self.variable is None:
            return None

        if value_class is None:
            value_class = self.variable.value_class

        if value_class.upper() in [
            "FLOAT",
            "FLOAT64",
            "DOUBLE",
            "FLOAT32",
            "SINGLE",
            "REAL",
            "FLOAT48",
        ]:
            return self.value_float64
        elif self.variable.scaling and not value_class.upper() in ["BOOL", "BOOLEAN"]:
            return self.value_float64
        elif value_class.upper() in ["UINT64"]:
            # moving the int64 range [2**63, 2**63 - 1] stored as a django
            # BigIntegerField to the int64 [0, 2**64 - 1]
            value = self.value_int64
            if value is None:
                return value
            return value + 2**63
        elif value_class.upper() in ["INT64", "UINT32", "DWORD", "INT48"]:
            return self.value_int64
        elif value_class.upper() in ["WORD", "UINT", "UINT16", "INT32"]:
            return self.value_int32
        elif value_class.upper() in ["INT16", "INT8", "UINT8"]:
            return self.value_int16
        elif value_class.upper() in ["BOOL", "BOOLEAN"]:
            return self.value_boolean
        else:
            logger.warning(
                f"The {value_class.upper()} variable value class is not defined in RecordedData value function. Default reading value as float."  # noqa: E501
            )
            return self.value_float64

    def save(self, *args, **kwargs):
        if self.date_saved is None:
            self.date_saved = now()
        super(RecordedData, self).save(*args, **kwargs)

    class Meta:
        db_table = "pyscada_recordeddata"
