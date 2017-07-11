#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import atexit
import os
import sys
from time import time
import win32serviceutil
import win32service
import win32event
import servicemanager
import socket

from django.core.management.base import BaseCommand

from pyscada.models import BackgroundTask


class Command(BaseCommand):
    args = 'daemon_name'
    help = 'Start a daemon for PyScada'

    def add_arguments(self, parser):
        parser.add_argument('daemon', choices=['event', 'export', 'mail'], nargs='+', type=str)

    def handle(self, *args, **options):

        daemon_name = options['daemon'][0]
        quit_command = 'CTRL-BREAK' if sys.platform == 'win32' else 'CONTROL-C'
        shutdown_message = 'exiting %s daemon' % daemon_name
        self.stdout.write("to stop the daemon press %s\n" % quit_command, ending='')
        atexit.register(self.program_cleanup)
        f = __import__('pyscada.%s.daemon' % daemon_name, fromlist=['a']).run
        try:
            f()
        except KeyboardInterrupt:
            self.stdout.write("%s\n" % shutdown_message, ending='')

    def program_cleanup(self, signum=None, frame=None):
        bt = BackgroundTask.objects.filter(pid=str(os.getpid())).last()
        if bt:
            bt.pid = 0
            bt.timestamp = time()
            bt.failed = False
            bt.done = True
            bt.message = 'done'
            bt.save()
            sys.exit(0)


class AppServerSvc(win32serviceutil.ServiceFramework):
    _svc_name_ = "PyScada Daemon Handler"
    _svc_display_name_ = "PyScada Daemon Handler"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.main()

    def main(self):
        pass


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(AppServerSvc)
