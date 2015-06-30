#!/usr/bin/python
# -*- coding: utf-8 -*-
from pyscada.models import BackgroundTask
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import os,sys
import signal
from time import time, sleep
import atexit

class Command(BaseCommand):
    args = 'daemon_name'
    help = 'Start a daemon for PyScada'

    def handle(self, *args, **options):
        if len(args)!=1:
            self.stdout.write("usage: python manage.py PyScadaWindowsDaemonHandler daemon_name\n", ending='')
        else:
            daemon_name = args[0]
            quit_command        = 'CTRL-BREAK' if sys.platform == 'win32' else 'CONTROL-C'
            shutdown_message    = 'exiting %s daemon'%daemon_name
            self.stdout.write("to stop the daemon press %s\n"% quit_command, ending='')
            atexit.register(self.program_cleanup)
            f = __import__('pyscada.%s.daemon'% daemon_name,fromlist=['a']).run
            try:
                f()
            except KeyboardInterrupt:
                self.stdout.write("%s\n"% shutdown_message, ending='')



    def program_cleanup(self,signum=None, frame=None):
        bt = BackgroundTask.objects.filter(pid = str(os.getpid())).last()
        if bt:
            bt.pid = 0
            bt.timestamp = time()
            bt.failed = False
            bt.done = True
            bt.message = 'done'
            bt.save()
            sys.exit(0)
