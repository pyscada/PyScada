import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import os
import sys




class AppServerSvc (win32serviceutil.ServiceFramework):
    _svc_name_ = "PyScada Mail Daemon"
    _svc_display_name_ = "PyScada Mail Daemon"
    _svc_description_ = "a PyScada Daemon for the Mail detection"
    def __init__(self,args):
        win32serviceutil.ServiceFramework.__init__(self,args)
        self.hWaitStop = win32event.CreateEvent(None,0,0,None)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "PyScadaServer.settings")
        import django
        django.setup()
        from pyscada.models import BackgroundTask
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

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_,''))
        self.main()

    def main(self):
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "PyScadaServer.settings")
        import django
        django.setup()
        from pyscada.mail import Handler
        from pyscada.utils import daemon_run
        daemon_run(
            label='pyscada.mail.daemon',
            handlerClass = Handler
            )
        

if __name__ == '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "PyScadaServer.settings")
    win32serviceutil.HandleCommandLine(AppServerSvc)
