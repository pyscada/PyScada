#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from pyscada.export.export import export_recordeddata_to_file
from pyscada.export.models import ScheduledExportTask, ExportTask
from pyscada.utils.scheduler import Process as BaseProcess
from pyscada.models import BackgroundProcess
from django.utils.timezone import now

from time import time, gmtime, mktime
from datetime import date, datetime, timedelta
from pytz import UTC
import json
import logging

logger = logging.getLogger(__name__)

try:
    import h5py
except:
    logger.error("Cannot import h5py", exc_info=True)
    pass


class ExportProcess(BaseProcess):
    def __init__(self, dt=5, **kwargs):
        self.job_id = 0
        super(ExportProcess, self).__init__(dt=dt, **kwargs)

    def loop(self):
        # todo try catch or filter.last()
        job = ExportTask.objects.get(pk=self.job_id)
        if job.file_format.upper() == "HDF5":
            file_ext = ".h5"
        elif job.file_format.upper() == "MAT":
            file_ext = ".mat"
        elif job.file_format.upper() == "CSV_EXCEL":
            file_ext = ".csv"
        else:
            return -1, None

        bp = BackgroundProcess.objects.filter(
            enabled=True,
            done=False,
            pid=self.pid,
            parent_process__pk=self.parent_process_id,
        ).first()

        if bp is None:
            logger.debug("export job %d no BP found" % self.job_id)
            return -1, None

        job.busy = True
        job.backgroundprocess = bp
        job.save()

        export_recordeddata_to_file(
            job.time_min(),
            job.time_max(),
            filename=None,
            active_vars=job.variables.values_list("pk", flat=True),
            file_extension=file_ext,
            filename_suffix=job.filename_suffix,
            backgroundprocess_id=bp.pk,
            export_task_id=job.pk,
            mean_value_period=job.mean_value_period,
        )
        job = ExportTask.objects.get(pk=job.pk)
        job.done = True
        job.busy = False
        job.datetime_finished = datetime.now(UTC)
        job.save()
        bp = BackgroundProcess.objects.filter(
            enabled=True,
            done=False,
            pid=self.pid,
            parent_process__pk=self.parent_process_id,
        ).first()

        if bp:
            bp.done = True
            bp.last_update = now()
            bp.message = "stopped"
            bp.save()

        return 0, None


class MasterProcess(BaseProcess):
    """
    handle the registration of new export tasks, and monitor running export tasks
    """

    def __init__(self, dt=5, **kwargs):
        super(MasterProcess, self).__init__(dt=dt, **kwargs)
        self._current_day = gmtime().tm_yday

    def loop(self):
        """
        this function will be called every self.dt_set seconds

        request data

        tm_wday 0=Monday
        tm_yday
        """
        today = date.today()
        # only start new jobs after change the day changed
        if self._current_day != gmtime().tm_yday:
            self._current_day = gmtime().tm_yday
            for job in ScheduledExportTask.objects.filter(
                active=1
            ):  # get all active jobs
                add_task = False
                if job.export_period == 1:  # daily
                    start_time = "%s %02d:00:00" % (
                        (today - timedelta(1)).strftime("%d-%b-%Y"),
                        job.day_time,
                    )  # "%d-%b-%Y %H:%M:%S"
                    start_time = mktime(
                        datetime.strptime(start_time, "%d-%b-%Y %H:%M:%S").timetuple()
                    )
                    filename_suffix = "daily_export_%d_%s" % (job.pk, job.label)
                    add_task = True
                elif (
                    job.export_period == 2 and gmtime().tm_yday % 2 == 0
                ):  # on even days (2,4,...)
                    start_time = "%s %02d:00:00" % (
                        (today - timedelta(2)).strftime("%d-%b-%Y"),
                        job.day_time,
                    )  # "%d-%b-%Y %H:%M:%S"
                    start_time = mktime(
                        datetime.strptime(start_time, "%d-%b-%Y %H:%M:%S").timetuple()
                    )
                    filename_suffix = "two_day_export_%d_%s" % (job.pk, job.label)
                    add_task = True
                elif (
                    job.export_period == 7 and gmtime().tm_wday == 0
                ):  # on every monday
                    start_time = "%s %02d:00:00" % (
                        (today - timedelta(7)).strftime("%d-%b-%Y"),
                        job.day_time,
                    )  # "%d-%b-%Y %H:%M:%S"
                    start_time = mktime(
                        datetime.strptime(start_time, "%d-%b-%Y %H:%M:%S").timetuple()
                    )
                    filename_suffix = "weekly_export_%d_%s" % (job.pk, job.label)
                    add_task = True
                elif (
                    job.export_period == 14 and gmtime().tm_yday % 14 == 0
                ):  # on every second monday
                    start_time = "%s %02d:00:00" % (
                        (today - timedelta(14)).strftime("%d-%b-%Y"),
                        job.day_time,
                    )  # "%d-%b-%Y %H:%M:%S"
                    start_time = mktime(
                        datetime.strptime(start_time, "%d-%b-%Y %H:%M:%S").timetuple()
                    )
                    filename_suffix = "two_week_export_%d_%s" % (job.pk, job.label)
                    add_task = True
                elif (
                    job.export_period == 30 and gmtime().tm_yday % 30 == 0
                ):  # on every 30 days
                    start_time = "%s %02d:00:00" % (
                        (today - timedelta(30)).strftime("%d-%b-%Y"),
                        job.day_time,
                    )  # "%d-%b-%Y %H:%M:%S"
                    start_time = mktime(
                        datetime.strptime(start_time, "%d-%b-%Y %H:%M:%S").timetuple()
                    )
                    filename_suffix = "30_day_export_%d_%s" % (job.pk, job.label)
                    add_task = True

                if job.day_time == 0:
                    end_time = "%s %02d:59:59" % (
                        (today - timedelta(1)).strftime("%d-%b-%Y"),
                        23,
                    )  # "%d-%b-%Y %H:%M:%S"
                else:
                    end_time = "%s %02d:59:59" % (
                        today.strftime("%d-%b-%Y"),
                        job.day_time - 1,
                    )  # "%d-%b-%Y %H:%M:%S"
                end_time = mktime(
                    datetime.strptime(end_time, "%d-%b-%Y %H:%M:%S").timetuple()
                )
                # create ExportTask
                if add_task:
                    et = ExportTask(
                        label=filename_suffix,
                        datetime_max=datetime.fromtimestamp(end_time, UTC),
                        datetime_min=datetime.fromtimestamp(start_time, UTC),
                        filename_suffix=filename_suffix,
                        mean_value_period=job.mean_value_period,
                        file_format=job.file_format,
                        datetime_start=datetime.fromtimestamp(end_time + 60, UTC),
                    )
                    et.save()

                    et.variables.add(*job.variables.all())

        # check running tasks and start the next Export Task
        running_jobs = ExportTask.objects.filter(busy=True, failed=False)
        if running_jobs:
            for job in running_jobs:
                if time() - job.start() < 30:
                    # only check Task when it is running longer then 30s
                    continue

                if job.backgroundprocess is None:
                    # if the job has no backgroundprocess assosiated mark as failed
                    job.failed = True
                    job.save()
                    continue

                if now() - timedelta(hours=1) > job.backgroundprocess.last_update:
                    # if the Background Process has been updated in the past 60s wait
                    continue

                if job.backgroundprocess.pid == 0:
                    # if the job has no valid pid mark as failed
                    job.failed = True
                    job.save()
                    continue

        else:
            # start the next Export Task
            job = ExportTask.objects.filter(
                done=False,
                busy=False,
                failed=False,
                datetime_start__lte=datetime.now(UTC),
            ).first()  # get all jobs
            if job:
                bp = BackgroundProcess(
                    label="pyscada.export-%d" % job.pk,
                    message="waiting..",
                    enabled=True,
                    parent_process_id=self.parent_process_id,
                    process_class="pyscada.export.worker.ExportProcess",
                    process_class_kwargs=json.dumps({"job_id": job.pk}),
                )
                bp.save()
                if job.datetime_start is None:
                    job.datetime_start = datetime.now(UTC)
                job.busy = True
                job.save()

        # delete all done jobs older the 60 days
        for job in ExportTask.objects.filter(
            done=True,
            busy=False,
            datetime_start__gte=datetime.fromtimestamp(time() + 60 * 24 * 60 * 60, UTC),
        ):
            job.delete()
        # delete all failed jobs older the 60 days
        for job in ExportTask.objects.filter(
            failed=True,
            datetime_start__gte=datetime.fromtimestamp(time() + 60 * 24 * 60 * 60, UTC),
        ):
            job.delete()

        return 1, None  # because we have no data to store
