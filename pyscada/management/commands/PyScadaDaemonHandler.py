#!/usr/bin/python
# -*- coding: utf-8 -*- 
from pyscada import log
from pyscada.models import BackgroundTask
from pyscada.utils import daemon_run

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import daemon
import os,sys
import signal
import daemon.pidfile
from time import time, sleep 
import traceback

class Command(BaseCommand):
    args = 'daemon_name {start | stop} '
    help = 'Start a daemon for PyScada'
    
    def handle(self, *args, **options):
        if len(args)!=2:
            self.stdout.write("usage: python manage.py PyScadaDaemonHandler daemonname {start | stop}\n", ending='')
        else:
            daemon_name = args[0]
            ## init
            context = self.init_context(daemon_name)
            
            # on start
            if 'start' == args[1]:
                self.start(context,daemon_name)
    
            # on stop
            elif 'stop' == args[1]:
                self.stop(context)
            else:
                self.stdout.write("Unknown command\nusage: python manage.py PyScadaDaemonHandler daemonname {start | stop }\n", ending='')
    
    
    def init_context(self,daemon_name):
        context = daemon.DaemonContext(
            working_directory=settings.BASE_DIR,
            pidfile=daemon.pidfile.PIDLockFile('%s%s.pid' % (settings.PID_ROOT , daemon_name)),
            )
        context.stdout = open('%s/%s.log'%(settings.PID_ROOT,daemon_name), "a+")
        context.signal_map = {
            signal.SIGTERM: self.program_cleanup,
            signal.SIGHUP: self.program_cleanup,
            #signal.SIGUSR1: reload_program_config,
            }
            
        # check the process
        if context.pidfile.is_locked():
            try:
                os.kill(context.pidfile.read_pid(), 0)
            except OSError:
                context.pidfile.break_lock()
        
        return context
    
    def start(self,context,daemon_name):
        if not context.pidfile.is_locked():
            try:
				mod = __import__('pyscada.%s'% daemon_name, fromlist=['Handler'])
				handlerClass = getattr(mod, 'Handler')
            except:
                self.stdout.write("no such daemon")
                var = traceback.format_exc()
                log.error("exeption while initialisation of %s:%s %s" % (daemon_name,os.linesep, var))
			
            context.open()
            daemon_run(
                label='pyscada.%s.daemon'% daemon_name,
                handlerClass = handlerClass
                )
        else:
            self.stdout.write("process is already runnging")  


    def stop(self,context=None):
        if context:
            pid = context.pidfile.read_pid()
            is_locked = context.pidfile.is_locked()
        else:
            is_locked = False
            pid = str(os.getpid())
            
        bt = BackgroundTask.objects.filter(pid=pid).last()
        if bt:
            # shudown the daemon process     
            bt.stop_daemon = 1
            bt.save()
            wait_count = 0
            while (wait_count < 60):
                bt = BackgroundTask.objects.filter(pid = pid).last()
                if bt:
                    if bt.done:
                        return
                else:
                    return
                wait_count += 1
                sleep(1)
                
        if is_locked:
            # kill the daemon process
            try:
                while 1:
                    os.kill(pid, 15)
                    sleep(0.1)
            except OSError, err:
                err = str(err)
                if err.find("No such process") > 0:
                    bt = BackgroundTask.objects.filter(pid = pid).last()
                    if bt:
                        bt.pid = 0
                        bt.done = True
                        bt.timestamp = time()
                        bt.message = 'force stopped'
                        bt.save()
        else:
            self.stdout.write("daemon is not running")
        
        
    def program_cleanup(self,signum=None, frame=None):
        bt = BackgroundTask.objects.filter(pid = str(os.getpid())).last()
        if bt:
            bt.pid = 0  
            bt.timestamp = time()
            bt.failed = True
            bt.message = 'external kill'
            bt.save()
            sys.exit(0)
    
