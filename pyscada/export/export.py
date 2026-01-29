# PyScada
from __future__ import unicode_literals

from pyscada.utils import validate_value_class

from pyscada.models import Variable, RecordedData, BackgroundProcess
from pyscada.export.hdf5_file import MatCompatibleH5
from pyscada.export.hdf5_file import unix_time_stamp_to_matlab_datenum
from pyscada.export.csv_file import ExcelCompatibleCSV
from pyscada.export.csv_file import unix_time_stamp_to_excel_datenum
from pyscada.export.models import ExportTask
from six import string_types

# Django
from django.conf import settings
from django.utils.timezone import now

# other
from datetime import datetime
import os
from time import time, strftime, mktime
from numpy import float64, float32, int32, uint16, int16, uint8, arange
import numpy as np
import math
import logging

logger = logging.getLogger(__name__)


def export_recordeddata_to_file(
    time_min=None,
    time_max=None,
    filename=None,
    active_vars=None,
    file_extension=None,
    append_to_file=False,
    no_mean_value=False,
    mean_value_period=5.0,
    backgroundprocess_id=None,
    export_task_id=None,
    **kwargs
):
    """
    read all data
    """
    if backgroundprocess_id is not None:
        tp = BackgroundProcess.objects.get(id=backgroundprocess_id)
        tp.message = "init"
        tp.last_update = now()
        tp.save()
    else:
        tp = None

    if isinstance(time_max, string_types):
        # convert date strings
        time_max = mktime(datetime.strptime(time_max, "%d-%m-%Y %H:%M:%S").timetuple())
    if isinstance(time_min, string_types):
        # convert date strings
        time_min = mktime(datetime.strptime(time_min, "%d-%m-%Y %H:%M:%S").timetuple())

    # add default time_min
    if time_max is None:
        time_max = time()  # now
    if time_min is None:
        time_min = time() - 24 * 60 * 60  # last 24 hours

    # add default extension if no extension is given
    if file_extension is None and filename is None:
        file_extension = ".h5"
    elif filename is not None:
        file_extension = "." + filename.split(".")[-1]
        filename = filename[: len(filename) - len(filename.split(".")[-1]) - 1]
    # validate file type
    if file_extension not in [".h5", ".mat", ".csv"]:
        if tp is not None:
            tp.last_update = now()
            tp.message = "failed wrong file type"
            tp.failed = True
            tp.save()

        if export_task_id is not None:
            job = ExportTask.objects.filter(pk=export_task_id).first()
            if job:
                job.failed = True
                job.save()
        return

    #
    if active_vars is None:
        active_vars = Variable.objects.filter(active=1, device__active=1)
    else:
        if type(active_vars) is str:
            if active_vars == "all":
                active_vars = Variable.objects.all()
            else:
                active_vars = Variable.objects.filter(active=1, device__active=1)
        else:
            active_vars = Variable.objects.filter(
                pk__in=active_vars, active=1, device__active=1
            )

    #
    if hasattr(settings, "PYSCADA_EXPORT"):
        if "output_folder" in settings.PYSCADA_EXPORT:
            backup_file_path = os.path.expanduser(
                settings.PYSCADA_EXPORT["output_folder"]
            )
        else:
            backup_file_path = os.path.expanduser("~/measurement_data_dumps")
    else:
        backup_file_path = os.path.expanduser("~/measurement_data_dumps")

    # add filename prefix
    backup_file_name = "measurement_data"
    if hasattr(settings, "PYSCADA_EXPORT"):
        if "file_prefix" in settings.PYSCADA_EXPORT:
            backup_file_name = settings.PYSCADA_EXPORT["file_prefix"] + backup_file_name
    # create output dir if not existing
    if not os.path.exists(backup_file_path):
        os.mkdir(backup_file_path)

    # filename  and suffix
    cdstr_from = datetime.fromtimestamp(time_min).strftime("%Y_%m_%d_%H%M")
    cdstr_to = datetime.fromtimestamp(time_max).strftime("%Y_%m_%d_%H%M")

    if filename is None:
        if "filename_suffix" in kwargs:
            filename = os.path.join(
                backup_file_path,
                backup_file_name
                + "_"
                + cdstr_from
                + "_"
                + cdstr_to
                + "_"
                + kwargs["filename_suffix"],
            )
        else:
            filename = os.path.join(
                backup_file_path, backup_file_name + "_" + cdstr_from + "_" + cdstr_to
            )
    else:
        filename = os.path.join(backup_file_path, filename)

    # check if file exists
    if os.path.exists(filename + file_extension) and not append_to_file:
        count = 0
        filename_old = filename
        while os.path.exists(filename + file_extension):
            filename = filename_old + "_%03.0f" % count
            count += 1

    # append the extension
    filename = filename + file_extension

    # add Filename to ExportTask
    if export_task_id is not None:
        job = ExportTask.objects.filter(pk=export_task_id).first()
        if job:
            job.filename = filename
            job.save()

    if mean_value_period == 0:
        no_mean_value = True
        mean_value_period = 5.0  # todo get from DB, default is 5 seconds

    # calculate time vector

    timevalues = arange(
        math.ceil(time_min / mean_value_period) * mean_value_period,
        math.floor(time_max / mean_value_period) * mean_value_period,
        mean_value_period,
    )

    # get Meta from Settings
    if hasattr(settings, "PYSCADA_META"):
        if "description" in settings.PYSCADA_META:
            description = settings.PYSCADA_META["description"]
        else:
            description = "None"
        if "name" in settings.PYSCADA_META:
            name = settings.PYSCADA_META["name"]
        else:
            name = "None"
    else:
        description = "None"
        name = "None"

    if file_extension == ".mat":
        bf = MatCompatibleH5(
            filename,
            version="1.1",
            description=description,
            name=name,
            creation_date=strftime("%d-%b-%Y %H:%M:%S"),
        )
        out_timevalues = [
            unix_time_stamp_to_matlab_datenum(element) for element in timevalues
        ]

    elif file_extension == ".h5":
        bf = MatCompatibleH5(
            filename,
            version="1.1",
            description=description,
            name=name,
            creation_date=strftime("%d-%b-%Y %H:%M:%S"),
        )
        out_timevalues = timevalues

    elif file_extension == ".csv":
        bf = ExcelCompatibleCSV(
            filename,
            version="1.1",
            description=description,
            name=name,
            creation_date=strftime("%d-%b-%Y %H:%M:%S"),
        )
        out_timevalues = [
            unix_time_stamp_to_excel_datenum(element) for element in timevalues
        ]

    else:
        return

    # less than 24
    # read everything
    bf.write_data(
        "time",
        float64(out_timevalues),
        id=0,
        description="global time vector",
        value_class=validate_value_class("FLOAT64"),
        unit="Days since 0000-1-1 00:00:00",
        color="#000000",
        short_name="time",
        chart_line_thickness=3,
    )

    for var_idx in range(0, active_vars.count(), 10):
        if tp is not None:
            tp.last_update = now()
            tp.message = "reading values from database (%d)" % var_idx
            tp.save()
        # query data
        var_slice = active_vars[var_idx : var_idx + 10]
        data = Variable.objects.query_datapoints(
            variable_ids=list(var_slice.values_list("pk", flat=True)),
            time_min=time_min,
            time_max=time_max,
            query_first_value=True,
        )

        for var in var_slice:
            # write background task info
            if tp is not None:
                tp.last_update = now()
                tp.message = "writing values for %s (%d) to file" % (var.name, var.pk)
                tp.save()
            # check if variable is scalled
            if var.scaling is None or var.value_class.upper() in ["BOOL", "BOOLEAN"]:
                value_class = var.value_class
            else:
                value_class = "FLOAT64"

            # read unit
            if hasattr(var.unit, "udunit"):
                udunit = var.unit.udunit
            else:
                udunit = "None"

            if var.pk not in data:
                # write dummy data
                bf.write_data(
                    var.name,
                    _cast_value(
                        [0] * len(timevalues), validate_value_class(value_class)
                    ),
                    id=var.pk,
                    description=var.description,
                    value_class=validate_value_class(value_class),
                    unit=udunit,
                    color=var.chart_line_color_code(),
                    short_name=var.short_name,
                    chart_line_thickness=var.chart_line_thickness,
                )
                if tp is not None:
                    tp.last_update = now()
                    tp.message = "no values for %s (%d) to file" % (var.name, var.pk)
                    tp.save()
                continue

            out_data = np.zeros(len(timevalues))
            # i                            # time data index
            ii = 0  # source data index
            # calculate mean values
            last_value = None
            max_ii = len(data[var.pk]) - 1
            for i in range(len(timevalues)):  # iter over time values
                if ii >= max_ii + 1:
                    # if not more data in data source break
                    if last_value is not None:
                        out_data[i] = last_value

                    continue
                # init mean value vars
                tmp = 0.0  # sum
                tmp_i = 0.0  # count

                if data[var.pk][ii][0] / 1000.0 < timevalues[i]:
                    # skip elements that are befor current time step
                    while data[var.pk][ii][0] / 1000.0 < timevalues[i] and ii < max_ii:
                        last_value = data[var.pk][ii][1]
                        ii += 1

                if ii >= max_ii:
                    if last_value is not None:
                        out_data[i] = last_value

                    continue

                # calc mean value
                if (
                    timevalues[i]
                    <= data[var.pk][ii][0] / 1000.0
                    < timevalues[i] + mean_value_period
                ):
                    # there is data in time range
                    while (
                        timevalues[i]
                        <= data[var.pk][ii][0] / 1000.0
                        < timevalues[i] + mean_value_period
                        and ii < max_ii
                    ):
                        # calculate mean value
                        if no_mean_value:
                            tmp = data[var.pk][ii][1]
                            tmp_i = 1
                        else:
                            tmp += data[var.pk][ii][1]
                            tmp_i += 1

                        last_value = data[var.pk][ii][1]
                        ii += 1
                    # calc and store mean value
                    if tmp_i > 0:
                        out_data[i] = tmp / tmp_i
                    else:
                        out_data[i] = data[var.pk][ii][1]
                        last_value = data[var.pk][ii][1]
                else:
                    # there is no data in time range, keep last value, not mean value
                    if last_value is not None:
                        out_data[i] = last_value

            # write data
            if file_extension == ".h5" or file_extension == ".mat":
                var_name = var.name.replace("/", "_")  # escape / character,
            else:
                var_name = var.name

            bf.write_data(
                var_name,
                _cast_value(out_data, validate_value_class(value_class)),
                id=var.pk,
                description=var.description,
                value_class=validate_value_class(value_class),
                unit=udunit,
                color=var.chart_line_color_code(),
                short_name=var.short_name,
                chart_line_thickness=var.chart_line_thickness,
            )

    bf.close_file()
    if tp is not None:
        tp.last_update = now()
        tp.message = "done"
        tp.done = True
        tp.save()


def _cast_value(value, _type):
    """
    cast value to _type
    """
    if _type.upper() == "FLOAT64":
        return float64(value)
    elif _type.upper() == "FLOAT32":
        return float32(value)
    elif _type.upper() == "INT32":
        return int32(value)
    elif _type.upper() == "UINT16":
        return uint16(value)
    elif _type.upper() == "INT16":
        return int16(value)
    elif _type.upper() == "BOOLEAN":
        return uint8(value)
    else:
        return float64(value)
