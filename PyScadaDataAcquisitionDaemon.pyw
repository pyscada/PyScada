#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import os,sys
from pyscada.daemon import Daemon

 
class MainDaemon(Daemon):
    def run(self):
        from pyscada.daemons.DataAcquisition import DataAcquisition as DAQ
        daq = DAQ()
        
if __name__ == "__main__":
    if len(sys.argv) == 3:
        sys.path.append(os.path.expanduser(sys.argv[1]))
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "PyScadaSite.settings")
        mdaemon = MainDaemon(os.path.join(os.path.expanduser(sys.argv[1]),'DataAcquisition-daemon.pid'))
        #mdaemon = MainDaemon('/tmp/DataAcquisition-daemon.pid')
        if 'start' == sys.argv[2]:
            mdaemon.start()
        elif 'stop' == sys.argv[2]:
            mdaemon.stop()
        elif 'restart' == sys.argv[2]:
            mdaemon.restart()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print 'usage: %s "path/to/Django/project/" start|stop|restart' % sys.argv[0]
        sys.exit(2)