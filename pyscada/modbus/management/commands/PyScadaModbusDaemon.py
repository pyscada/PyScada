#!/usr/bin/python
# -*- coding: utf-8 -*- 
from pyscada import log
from pyscada.daemon import Daemon
from pyscada.modbus.client import DataAcquisition as DAQ
from django.core.management.base import BaseCommand, CommandError
from pyscada.models import TaskProgress
from django.conf import settings
import os,sys
from time import sleep,time
import traceback

class Command(BaseCommand):
    args = 'start | stop | restart'
    help = 'Start the data aquisition daemon for PyScada'

    def handle(self, *args, **options):
        
        if len(args)!=1:
            self.stdout.write("usage: python manage.py PyScadaDaemon start | stop | restart\n", ending='')
        else:
            mdaemon = MainDaemon('%s%s'%(settings.PYSCADA_MODBUS['pid_file'],settings.PROJECT_PATH)
            if 'start' == args[0]:
                log.info("try starting dataaquisition daemon")
                mdaemon.start()
            elif 'stop' == args[0]:
                log.info("try stopping dataaquisition daemon")
                try:
                    pf = file(mdaemon.pidfile,'r')
                    pid = int(pf.read().strip())
                    pf.close()
                except IOError:
                    pid = None
                if pid:
                    wait_count = 0
                    tp = TaskProgress.objects.filter(pid=pid).last()
                    if tp:
                        tp.stop_daemon = 1
                        tp.save()
                        while (wait_count < 10 and not tp.done):
                            tp = TaskProgress.objects.filter(pid=pid).last()
                            wait_count += 1
                            sleep(1)
                    
                mdaemon.stop()
                log.notice("stopped  dataaquisition daemon")
            elif 'restart' == args[0]:
                log.info("try restarting data aquisition daemon")
                try:
                    pf = file(mdaemon.pidfile,'r')
                    pid = int(pf.read().strip())
                    pf.close()
                except IOError:
                    pid = None
                if pid:
                    wait_count = 0
                    tp = TaskProgress.objects.filter(pid=pid).last()
                    if tp:
                        tp.stop_daemon = 1
                        tp.save()
                        while (wait_count < 10 and not tp.done):
                            tp = TaskProgress.objects.filter(pid=pid).last()
                            wait_count += 1
                            sleep(1)
                mdaemon.stop()
                mdaemon.start()
            else:
                self.stdout.write("Unknown command", ending='')

class MainDaemon(Daemon):
    def run(self):
        try:
            pf = file(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = 0
        
        tp = TaskProgress(start=time(),label='data acquision daemon',message='init',timestamp=time(),pid = pid)
        tp.save()
        tp_id = tp.id
        
        try:
            daq = DAQ()
        except:
            var = traceback.format_exc()
            log.error("exeption in dataaquisition daemon, %s" % var)
            tp.message = 'failed'
            tp.failed = True
            tp.timestamp = time()
            tp.save()
            raise
        tp.message = 'running...'
        tp.save()
        log.notice("started dataaquisition daemon")
        while not tp.stop_daemon:
            try:
                dt = daq.run()
            except:
                var = traceback.format_exc()
                log.debug("exeption in dataaquisition daemon, %s" % var,-1)
                daq = DAQ()
                dt = float(settings.PYSCADA_MODBUS['stepsize'])
            tp = TaskProgress.objects.get(id=tp_id)    
            tp.timestamp = time()
            tp.load= 1.-max(min(dt/daq._dt,1),0)
            tp.save()
            if dt>0:
                sleep(dt)
        try:
            tp = TaskProgress.objects.get(id=tp_id)    
            tp.done = True
            tp.message = 'stopped'
            tp.timestamp = time()
            tp.save()
        except:
            var = traceback.format_exc()
            log.debug("exeption in dataaquisition daemon, %s" % var,-1)
        log.notice("stopped dataaquisition daemon execution")
        self.stop()


