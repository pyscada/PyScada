#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import signal
import sys
import traceback
from time import time, sleep

import daemon
import daemon.pidfile
from django.conf import settings
from django.core.management.base import BaseCommand

from pyscada import log
from pyscada.models import BackgroundTask
from pyscada.utils import daemon_run


class Command(BaseCommand):
    help = 'Start a daemon for PyScada'

    def add_arguments(self, parser):
        parser.add_argument('daemon', choices=['event', 'export', 'mail'], nargs='+', type=str)
        parser.add_argument('action', choices=['start', 'stop'], nargs='+', type=str)

    def handle(self, *args, **options):

        daemon_name = options['daemon'][0]
        # init
        context = self.init_context(daemon_name)

        # on start
        if 'start' == options['action'][0]:
            self.start(context, daemon_name)
        # on stop
        elif 'stop' == options['action'][0]:
            self.stop(context)

    def init_context(self, daemon_name):
        # chek write permission to the pid and log dir
        if not os.access('/tmp/', os.W_OK):
            self.stdout.write("pid path is not writeable")
            sys.exit(0)
        if os.access('/tmp/pyscada_daemon_%s.pid' % daemon_name, os.F_OK) and not os.access(
                        '/tmp/pyscada_daemon_%s.pid' % daemon_name, os.W_OK):
            self.stdout.write("pid file is not writeable")
            sys.exit(0)
        if not os.access(settings.BASE_DIR, os.W_OK):
            self.stdout.write("log path is not writeable")
            sys.exit(0)
        context = daemon.DaemonContext(
            working_directory=settings.BASE_DIR,
            pidfile=daemon.pidfile.PIDLockFile('/tmp/pyscada_daemon_%s.pid' % daemon_name),
        )
        context.stdout = open('%s/%s.log' % (settings.BASE_DIR, daemon_name), "a+")
        context.signal_map = {
            signal.SIGTERM: self.program_cleanup,
            signal.SIGHUP: self.program_cleanup,
            # signal.SIGUSR1: reload_program_config,
        }

        # check the process
        if context.pidfile.is_locked():
            try:
                os.kill(context.pidfile.read_pid(), 0)
            except OSError:
                context.pidfile.break_lock()

        return context

    def start(self, context, daemon_name):
        if not context.pidfile.is_locked():
            try:
                mod = __import__('pyscada.%s.handler' % daemon_name, fromlist=['Handler'])
                handler_class = getattr(mod, 'Handler')
            except:
                self.stdout.write("no such daemon")
                var = traceback.format_exc()
                log.error("exeption while initialisation of %s:%s %s" % (daemon_name, os.linesep, var))
                return

            context.open()
            daemon_run(
                label='pyscada.%s.daemon' % daemon_name,
                handlerClass=handler_class
            )
        else:
            self.stdout.write("process is already runnging")

    def stop(self, context=None):
        if context:
            pid = context.pidfile.read_pid()
            is_locked = context.pidfile.is_locked()
        else:
            is_locked = False
            pid = str(os.getpid())

        bt = BackgroundTask.objects.filter(pid=pid).last()
        if bt:
            # shutdown the daemon process
            bt.stop_daemon = 1
            bt.save()
            bt_id = bt.pk
            wait_count = 0
            while wait_count < 60:
                bt = BackgroundTask.objects.filter(pk=bt_id).last()
                if bt:
                    if bt.done:
                        return
                else:
                    return
                wait_count += 1
                sleep(1)

        # update is_locked status
        if context:
            is_locked = context.pidfile.is_locked()

        if is_locked:
            # kill the daemon process
            try:
                while 1:
                    os.kill(pid, 15)
                    sleep(0.1)
            except OSError as err:
                err = str(err)
                if err.find("No such process") > 0:
                    bt = BackgroundTask.objects.filter(pid=pid).last()
                    if bt:
                        bt.pid = 0
                        bt.done = True
                        bt.timestamp = time()
                        bt.message = 'force stopped'
                        bt.save()
        else:
            self.stdout.write("daemon is not running")

    def program_cleanup(self, signum=None, frame=None):
        bt = BackgroundTask.objects.filter(pid=str(os.getpid())).last()
        if bt:
            bt.pid = 0
            bt.timestamp = time()
            bt.failed = True
            bt.message = 'external kill'
            bt.save()
            sys.exit(0)
