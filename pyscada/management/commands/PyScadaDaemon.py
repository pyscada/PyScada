#!/usr/bin/python
# -*- coding: utf-8 -*- 
from pyscada import log
from pyscada.daemon import Daemon
from pyscada.daemons.DataAcquisition import DataAcquisition as DAQ
from django.core.management.base import BaseCommand, CommandError
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
            mdaemon = MainDaemon('%s/DataAcquisition-daemon.pid'%settings.PROJECT_PATH)
            if 'start' == args[0]:
                log.info("try starting data aquisition daemon")
                mdaemon.start()
                
            elif 'stop' == args[0]:
                log.info("try stopping data aquisition daemon")
                mdaemon.stop()
                log.notice("stopped  dataaquisition daemon")
            elif 'restart' == args[0]:
                log.info("try restarting data aquisition daemon")
                mdaemon.restart()
            else:
                self.stdout.write("Unknown command", ending='')

class MainDaemon(Daemon):
    def run(self):
        try:
            daq = DAQ()
        except:
            var = traceback.format_exc()
            log.error("exeption in dataaquisition daemnon, %s" % var)
            raise
        
        tomorrow = (round(time()/24/60/60)+1)*24*60*60
        log.notice("started dataaquisition daemon")
        while True:
            if time()>tomorrow:
                tomorrow = (round(time()/24/60/60)+1)*24*60*60
            try:
                dt = daq.run()
            except:
                var = traceback.format_exc()
                log.debug("exeption in dataaquisition daemnon, %s" % var,-1)
                daq = DAQ()
                dt = 5
            
            if dt>0:
                sleep(dt)
        log.notice("stoped daemon execution")

