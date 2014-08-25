#!/usr/bin/python
# -*- coding: utf-8 -*- 
from pyscada import log
from pyscada.daemon import Daemon
from pyscada.modbus import client
from django.core.management.base import BaseCommand, CommandError
from pyscada.models import BackgroundTask
from django.conf import settings
import os,sys
from time import sleep,time
import traceback

class Command(BaseCommand):
    args = 'start | stop | restart'
    help = 'Start the modbus data aquisition daemon for PyScada'

    def handle(self, *args, **options):
        
        if len(args)!=1:
            self.stdout.write("usage: python manage.py PyScadaModbusDaemon start | stop | restart\n", ending='')
        else:
            if not os.path.exists(settings.PID_ROOT):
                os.makedirs(settings.PID_ROOT)
            mdaemon = MainDaemon('%s%s'%(settings.PID_ROOT,settings.PYSCADA_MODBUS['pid_file_name']))
            if 'start' == args[0]:
                log.info("try starting dataaquisition daemon")
                try:
                    pf = file(mdaemon.pidfile,'r')
                    pid = int(pf.read().strip())
                    pf.close()
                except IOError:
                    pid = None
                
                if pid:
                     # Check For the existence of a unix pid.
                    try:
                        os.kill(pid, 0)
                    except OSError:
                        # daemon is dead delete file and mark taskprogress as failed
                        tp = BackgroundTask.objects.filter(pid=pid).last()
                        if tp:
                            tp.failed = True
                            tp.save()
                        os.remove(mdaemon.pidfile)
                else:
                    # check for dead tasks in taskprogress list
                    for task in BackgroundTask.objects.filter(done=False,failed=False):
                        if task.pid >0:
                            try:
                                os.kill(task.pid, 0)
                            except OSError:
                                # daemon is dead delete file and mark taskprogress as failed
                                task.failed = True
                                task.save()
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
                    tp = BackgroundTask.objects.filter(pid=pid).last()
                    if tp:
                        tp.stop_daemon = 1
                        tp.save()
                        while (wait_count < 10 and not tp.done):
                            tp = BackgroundTask.objects.filter(pid=pid).last()
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
                    tp = BackgroundTask.objects.filter(pid=pid).last()
                    if tp:
                        tp.stop_daemon = 1
                        tp.save()
                        while (wait_count < 10 and not tp.done):
                            tp = BackgroundTask.objects.filter(pid=pid).last()
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
        
        tp = BackgroundTask(start=time(),label='data acquision daemon',message='init',timestamp=time(),pid = pid)
        tp.save()
        tp_id = tp.id
        
        try:
            daq = client.DataAcquisition()
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
                daq = client.DataAcquisition()
                dt = 5
            tp = BackgroundTask.objects.get(id=tp_id)    
            tp.timestamp = time()
            tp.load= 1.-max(min(dt/daq._dt,1),0)
            tp.save()
            if dt>0:
                sleep(dt)
        try:
            tp = BackgroundTask.objects.get(id=tp_id)    
            tp.done = True
            tp.message = 'stopped'
            tp.timestamp = time()
            tp.save()
        except:
            var = traceback.format_exc()
            log.debug("exeption in dataaquisition daemon, %s" % var,-1)
        log.notice("stopped dataaquisition daemon execution")
        self.stop()


