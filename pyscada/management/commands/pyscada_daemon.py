#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from pyscada.utils.scheduler import Scheduler
from pyscada.models import BackgroundProcess
from pyscada.utils import datetime_now
from django.core.management.base import BaseCommand
from django.conf import settings
import os
import signal
import errno



class Command(BaseCommand):
    help = 'Manage the Background Process Daemon for PyScada'

    def add_arguments(self, parser):
        parser.add_argument('action', choices=['start', 'stop', 'status', 'init'], nargs='+', type=str)
        
    def handle(self, *args, **options):
        
        # init
        scheduler = Scheduler(stdout=self.stdout)
        # on start
        if 'start' == options['action'][0]:
            scheduler.start()
        # on stop
        elif 'stop' == options['action'][0]:
            if scheduler.read_pid() is not None:
                try:
                    os.kill(scheduler.read_pid(), signal.SIGTERM)
                except OSError as e:
                    pass
            self._check_processlist()


        elif 'status' == options['action'][0]:
            scheduler.status()
        elif 'init' == options['action'][0]:
            # first delete all old processes in processlist
            # todo  check for running processes befor deletion
            self._check_processlist()
            BackgroundProcess.objects.all().delete()
            # add the Scheduler Process
            parent_process = BackgroundProcess(pk=1, label='pyscada.utils.scheduler.Scheduler',
                                               enabled=True,
                                               process_class='pyscada.utils.scheduler.Process')
            parent_process.save()
            # check for processes to add in init block of each app
            for app in settings.INSTALLED_APPS:
                m = __import__(app, fromlist=[''])
                if hasattr(m, 'parent_process_list'):
                    for process in m.parent_process_list:
                        if 'enabled' not in process:
                            process['enabled'] = True
                        if 'parent_process' not in process:
                            process['parent_process'] = parent_process
                        bp = BackgroundProcess(**process)
                        bp.save()

    def _check_processlist(self, sig=signal.SIGTERM):
        # check if all processes are stopped
        for process in BackgroundProcess.objects.filter(done=False, pid__gt=0):
            try:
                os.kill(process.pid, sig)
            except OSError as e:
                if e.errno == errno.ESRCH:  # no such process
                    process.message = 'stopped'
                    process.pid = 0
                    process.last_update = datetime_now()
                    process.save()
                elif e.errno == errno.EPERM:  # Operation not permitted
                    self.stdout.write("can't stop process %d: %s with pid %d, 'Operation not permitted'" % (
                        process.pk, process.label, process.pid))