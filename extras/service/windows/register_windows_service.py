import win32serviceutil
import win32service
import win32event
import servicemanager
import os




class AppServerSvc (win32serviceutil.ServiceFramework):
    _svc_name_ = "PyScada Daemon"
    _svc_display_name_ = "PyScada Daemon"
    _svc_description_ = "a PyScada Daemon for the detection"
    def __init__(self,args):
        win32serviceutil.ServiceFramework.__init__(self,args)
        self.hWaitStop = win32event.CreateEvent(None,0,0,None)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "PyScadaServer.settings")
        import django
        django.setup()
        # todo implement
        raise NotImplementedError

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_,''))
        self.main()

    def main(self):
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "PyScadaServer.settings")
        import django
        django.setup()
        # todo implement
        raise NotImplementedError

if __name__ == '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "PyScadaServer.settings")
    win32serviceutil.HandleCommandLine(AppServerSvc)
