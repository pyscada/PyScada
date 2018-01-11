#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
 - > master_process
    - > mail master
    - > export master
     - > export task A
     - > export task B
    - > event master
    
    - > modbus master(registers a process for every device/port)
     - > modbus device A (IP 1)
     - > modbus device B (IP 2)
     - > modbus device C, D (RTU, TTY1)
     - > modbus device E, F (RTU, TTY2)
    - > onewire (registers a process for every device/port)
     - > onewire device G, H (server a)
    - > visa (registers a process for every device/port)
     - > visa device A
    - > systemstat master
    - > smbus (registers a process for every device/port)
    - > jofra350 (registers a process for every device/port)
    

"""
from __future__ import unicode_literals

import atexit
import errno
from os import linesep, umask, access, W_OK, kill, remove, setsid, path, fork, F_OK, WNOHANG, getpid, waitpid
import signal
import sys
import traceback
from time import time, sleep
from datetime import datetime

from django import db
from django.conf import settings

from pyscada.models import BackgroundProcess, DeviceWriteTask, Device, RecordedData
from pyscada.utils import datetime_now
import logging

logger = logging.getLogger(__name__)


class Scheduler(object):
    """
    Manages and monitor all the sub processes.
    """
    PROCESSES = {}
    SIG_QUEUE = []
    SIGNALS = [signal.SIGTERM, signal.SIGUSR1, signal.SIGHUP, signal.SIGUSR2]

    def __init__(self, daemon_name='pyscada.utils.scheduler.Scheduler',
                 run_as_daemon=True, stdout=sys.stdout, stdin=sys.stdin, stderr=sys.stderr,
                 pid_file_name='/tmp/pyscada_daemon.pid'):
        """
        
        """
        self.pid_file_name = pid_file_name
        self.run_as_daemon = run_as_daemon

        self.pid = None
        self.process_id = None
        self.stdout = stdout
        self.stdin = stdin
        self.stderr = stderr

        if not access(path.dirname(self.pid_file_name), W_OK) and self.run_as_daemon:
            self.stdout.write("pidfile path is not writeable\n")
            sys.exit(0)
        if access(self.pid_file_name, F_OK) and not access(self.pid_file_name, W_OK) and self.run_as_daemon:
            self.stdout.write("pidfile file is not writeable\n")
            sys.exit(0)

        self.label = daemon_name

    def init_db(self, sig=0):
        """

        """
        for process in BackgroundProcess.objects.filter(done=False, pid__gt=0):
            try:
                kill(process.pid, sig)
                self.stderr.write("init db aborted, at least one process is alive\n")
                return False
            except OSError as e:
                if e.errno == errno.ESRCH:  # no such process
                    process.message = 'stopped'
                    process.pid = 0
                    process.last_update = datetime_now()
                    process.save()
                elif e.errno == errno.EPERM:  # Operation not permitted
                    self.stderr.write("can't stop process %d: %s with pid %d, 'Operation not permitted'\n" % (
                        process.pk, process.label, process.pid))

        BackgroundProcess.objects.all().delete()
        # add the Scheduler Process
        parent_process = BackgroundProcess(pk=1, label='pyscada.utils.scheduler.Scheduler',
                                           enabled=True,
                                           process_class='pyscada.utils.scheduler.Process')
        parent_process.save()
        # check for processes to add in init block of each app
        for app in settings.INSTALLED_APPS:
            m = __import__(app, fromlist=[str('a')])
            self.stderr.write("app %s\n" % app)
            if hasattr(m, 'parent_process_list'):
                for process in m.parent_process_list:
                    self.stderr.write("add %s\n" % process['label'])
                    if 'enabled' not in process:
                        process['enabled'] = True
                    if 'parent_process' not in process:
                        process['parent_process'] = parent_process
                    bp = BackgroundProcess(**process)
                    bp.save()

        self.stderr.write("init db completed\n")
        return True

    def demonize(self):
        """
        do the double fork magic
        """
        # check if a process is already running
        if access(self.pid_file_name, F_OK):
            # read the pid file
            pid = self.read_pid()

            try:
                kill(pid, 0)  # check if process is running
                self.stderr.write("process is already running\n")
                return False
            except OSError as e:
                if e.errno == errno.ESRCH:
                    # process is dead
                    self.delete_pid(force_del=True)
                else:
                    self.stderr.write("demonize failed, something went wrong: %d (%s)\n" % (e.errno, e.strerror))
                    return False

        try:
            pid = fork()
            if pid > 0:
                # Exit from the first parent
                timeout = time() + 60
                while self.read_pid() is None:
                    self.stderr.write("waiting for pid..\n")
                    sleep(0.5)
                    if time() > timeout:
                        break
                self.stderr.write("pid is %d\n" % self.read_pid())
                sys.exit(0)
        except OSError as e:
            self.stderr.write("demonize failed in 1. Fork: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        # Decouple from parent environment
        # os.chdir("/")
        setsid()
        umask(0)

        # Do the Second fork
        try:
            pid = fork()
            if pid > 0:
                # Exit from the second parent
                sys.exit(0)
        except OSError as e:
            self.stderr.write("demonize failed in 2. Fork: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        # Redirect standard file descriptors
        # sys.stdout.flush()
        # sys.stderr.flush()
        # si = file(self.stdin, 'r')
        # so = file(self.stdout, 'a+')
        # se = file(self.stderr, 'a+',
        # os.dup2(si.fileno(), sys.stdin.fileno())
        # os.dup2(so.fileno(), sys.stdout.fileno())
        # os.dup2(se.fileno(), sys.stderr.fileno())

        # Write the PID file
        atexit.register(self.delete_pid)
        self.write_pid()
        return True

    def write_pid(self, pid=None):
        if pid is None:
            pid = getpid()
        with open(self.pid_file_name, 'w+') as f:
            f.write('%d\n' % pid)
        logger.info('created pid %d' % pid)

    def read_pid(self):
        if not access(self.pid_file_name, F_OK):
            return None

        with open(self.pid_file_name, 'r') as f:
            pid = int(f.read().strip())
        return pid

    def delete_pid(self, force_del=False):
        """
        delete the pid file
        """
        pid = self.read_pid()
        if pid != getpid() or force_del:
            logger.debug('process %d tried to delete pid' % getpid())
            return False

        if access(self.pid_file_name, F_OK):
            try:
                remove(self.pid_file_name)  # remove the old pid file
                logger.debug('delete pid (%d)' % getpid())
            except:
                logger.debug("can't delete pid file")

    def start(self):
        """
        start the scheduler
        """
        #  demonize
        if self.run_as_daemon:
            if not self.demonize():
                sys.exit(0)

        master_process = BackgroundProcess.objects.filter(parent_process__isnull=True,
                                                          label=self.label,
                                                          enabled=True).first()
        self.pid = getpid()
        if not master_process:
            self.delete_pid(force_del=True)
            logger.debug('no such process in BackgroundProcesses\n')
            sys.exit(0)

        self.process_id = master_process.pk
        master_process.pid = self.pid
        master_process.last_update = datetime_now()
        master_process.running_since = datetime_now()
        master_process.done = False
        master_process.failed = False
        master_process.message = 'init master process'
        master_process.save()
        BackgroundProcess.objects.filter(parent_process__pk=self.process_id, done=False).update(message='stopped')
        # register signals
        [signal.signal(s, self.signal) for s in self.SIGNALS]
        #signal.signal(signal.SIGCHLD, self.handle_chld)
        # start the main loop
        self.run()
        sys.exit(0)

    def run(self):
        """
        the main loop
        """
        try:
            master_process = BackgroundProcess.objects.filter(pk=self.process_id).first()
            if master_process:
                master_process.last_update = datetime_now()
                master_process.message = 'init child processes'
                master_process.save()
            else:
                self.delete_pid(force_del=True)
                self.stderr.write("no such process in BackgroundProcesses")
                sys.exit(0)

            self.manage_processes()
            while True:
                # handle signals
                sig = self.SIG_QUEUE.pop(0) if len(self.SIG_QUEUE) else None
                BackgroundProcess.objects.filter(pk=self.process_id).update(
                    last_update=datetime_now(),
                    message='running..')
                if sig is None:
                    self.manage_processes()
                elif sig not in self.SIGNALS:
                    logger.error('%s, unhandled signal %d' % (self.label, sig))
                    continue
                elif sig == signal.SIGTERM:
                    logger.debug('%s, termination signal' % self.label)
                    raise StopIteration
                elif sig == signal.SIGHUP:
                    # todo handle sighup
                    pass
                elif sig == signal.SIGUSR1:
                    # restart all child processes
                    self.restart()
                elif sig == signal.SIGUSR2:
                    # write the process status to stdout
                    self.status()
                    pass
                sleep(5)
        except StopIteration:
            self.stop()
            sys.exit(0)
        except SystemExit:
            raise
        except:
            logger.error('%s(%d), unhandled exception\n%s' % (self.label, getpid(), traceback.format_exc()))

    def manage_processes(self):
        """
        
        """
        # check for new processes to spawn
        process_list = []
        for process in BackgroundProcess.objects.filter(parent_process__pk=self.process_id):
            process_list.append(process)
            process_list += list(process.backgroundprocess_set.filter())

        for process in process_list:
            #
            if not process.enabled or not process.parent_process.enabled or process.done:
                if process.pk in self.PROCESSES:
                    self.kill_process(process.pk)
                    continue
                continue

            if process.pk in self.PROCESSES:
                continue

            if process.parent_process.pk not in self.PROCESSES and process.parent_process.pk != self.process_id:
                continue

            # spawn new process
            process_inst = process.get_process_instance()
            if process_inst is not None:
                self.spawn_process(process_inst)
                logger.debug('process %s started' % process.label)
            else:
                logger.debug('process %s returned None' % process.label)

        # check all running processes
        process_list = list(self.PROCESSES.values())
        for process in process_list:
            try:
                kill(process.pid, 0)
            except OSError as e:
                if e.errno == errno.ESRCH:
                    logger.debug('process %d is dead' % process.process_id)

                    try:
                        self.PROCESSES.pop(process.process_id)
                    except:
                        pass
                    # process is dead, delete process
                    if process.parent_process_id == self.process_id:
                        p = BackgroundProcess.objects.filter(pk=process.process_id).first()
                        if p:
                            p.pid = 0
                            p.last_update = datetime_now()
                            p.failed = True
                            p.save()
                    else:
                        # delete grandchild process
                        BackgroundProcess.objects.filter(pk=process.process_id).delete()

    def handle_chld(self, sig, frame):
        """
        SIGCHLD handling
        :param sig:
        :param frame:
        :return:
        """
        try:
            while True:
                wpid, status = waitpid(-1, WNOHANG)
                if not wpid:
                    break
                    # self.stdout.write('%d,%d\n' % (wpid, status))
        except:
            pass

    def restart(self):
        """
        restart all child processes
        """
        BackgroundProcess.objects.filter(pk=self.process_id).update(
            last_update=datetime_now(),
            message='restarting..')
        timeout = time() + 60  # wait max 60 seconds
        self.kill_processes(signal.SIGTERM)
        while self.PROCESSES and time() < timeout:
            sleep(0.1)
        self.kill_processes(signal.SIGKILL)
        self.manage_processes()

    def stop(self, sig=signal.SIGTERM):
        """
        stop the scheduler and stop all processes
        """

        if self.pid is None:
            self.pid = self.read_pid()
        if self.pid is None:
            sp = BackgroundProcess.objects.filter(pk=1).first()
            if sp:
                self.pid = sp.pid
        if self.pid is None or self.pid == 0:
            logger.error("can't determine process id exiting.")
            return False
        if self.pid != getpid():
            # calling from outside the daemon instance
            logger.debug('send sigterm to daemon')
            try:
                kill(self.pid, sig)
                return True
            except OSError as e:
                if e.errno == errno.ESRCH:
                    return False
                else:
                    return False

        logger.debug('start termination of the daemon')
        BackgroundProcess.objects.filter(pk=self.process_id).update(
            last_update=datetime_now(),
            message='stopping..')

        timeout = time() + 60  # wait max 60 seconds
        self.kill_processes(signal.SIGTERM)
        while self.PROCESSES and time() < timeout:
            self.kill_processes(signal.SIGTERM)
            sleep(1)
        self.kill_processes(signal.SIGKILL)
        BackgroundProcess.objects.filter(pk=self.process_id).update(
            last_update=datetime_now(),
            message='stopped')
        logger.debug('termination of the daemon done')
        return True

    def kill_process(self, process_id, sig=signal.SIGTERM):
        """
        
        """
        p = self.PROCESSES[process_id]
        try:
            kill(p.pid, sig)
            logger.debug('try to terminate process id %d' % p.pid)
        except OSError as e:
            if e.errno == errno.ESRCH:
                try:
                    self.PROCESSES.pop(process_id)
                    logger.debug('%s: process id %d is terminated' % p.pid)
                    return
                except:
                    return
        try:
            while True:
                wpid, status = waitpid(p.pid, WNOHANG)
                if not wpid:
                    break
                    # self.stdout.write('%d,%d\n' % (wpid, status))
        except:
            pass


    def kill_processes(self, sig=signal.SIGTERM):
        """
        
        """
        process_ids = list(self.PROCESSES.keys())
        for process_id in process_ids:
            self.kill_process(process_id, sig)

    def spawn_process(self, process=None):
        """
        spawn a new process
        """
        if process is None:
            return False
        # start new child process
        pid = fork()
        if pid != 0:
            # parent process
            process.pid = pid
            self.PROCESSES[process.process_id] = process
            db.connections.close_all()
            return True

        # child process
        process.pid = getpid()
        process.pre_init_process()
        process.init_process()
        process.run()
        sys.exit(0)

    def status(self):
        """
        write the current daemon status to stdout
        """

        if self.pid is None:
            self.pid = self.read_pid()
        if self.pid is None:
            sp = BackgroundProcess.objects.filter(pk=1).first()
            if sp:
                self.pid = sp.pid
        if self.pid is None or self.pid == 0:
            self.stderr.write("%s: can't determine process id exiting.\n" % datetime.now().isoformat(b' '))
            return False
        if self.pid != getpid():
            # calling from outside the daemon instance
            try:
                kill(self.pid, signal.SIGUSR2)
                return True
            except OSError as e:
                if e.errno == errno.ESRCH:
                    return False
                else:
                    return False

        process_list = []
        for process in BackgroundProcess.objects.filter(parent_process__pk=self.process_id):
            process_list.append(process)
            process_list += list(process.backgroundprocess_set.filter())
        for process in process_list:
            logger.debug('%s, parrent process_id %d' % (self.label, process.parent_process.pk))
            logger.debug('%s, process_id %d' % (self.label, self.process_id))

    def signal(self, signum=None, frame=None):
        """
        handle signals
        """
        self.SIG_QUEUE.append(signum)


class Process(object):
    def __init__(self, dt=5, **kwargs):
        self.pid = None
        self.dt_set = dt
        self.process_id = 0
        self.parent_process_id = 0
        self.label = ''
        # register signals
        self.SIG_QUEUE = []
        self.SIGNALS = [signal.SIGTERM, signal.SIGUSR1, signal.SIGHUP, signal.SIGUSR2]
        #
        for key, value in kwargs.items():
            setattr(self, key, value)

    def pre_init_process(self):
        """
        will be executed after process fork
        """
        db.connections.close_all()
        # update process info
        BackgroundProcess.objects.filter(pk=self.process_id).update(
            pid=self.pid,
            last_update=datetime_now(),
            running_since=datetime_now(),
            done=False,
            failed=False,
            message='init process..',
        )

        [signal.signal(s, signal.SIG_DFL) for s in self.SIGNALS]  # reset
        [signal.signal(s, self.signal) for s in self.SIGNALS]  # set

    def init_process(self):
        """
        override this.
        """
        return True

    def run(self):
        BackgroundProcess.objects.filter(pk=self.process_id).update(last_update=datetime_now(), message='running..')

        try:
            while True:
                t_start = time()
                # handle signals
                sig = self.SIG_QUEUE.pop(0) if len(self.SIG_QUEUE) else None
                # update progress
                BackgroundProcess.objects.filter(pk=self.process_id).update(last_update=datetime_now())
                if sig is None:
                    # run loop action
                    status, data = self.loop()
                    if data is not None:
                        # write data to the database
                        for item in data:
                            RecordedData.objects.bulk_create(item)
                    if status == 1: # Process OK
                        pass
                    elif status == -1:
                        # some thing went wrong
                        # todo handle
                        raise StopIteration
                    elif status == 0:
                        # loop is done exit
                        raise StopIteration
                    else:
                        pass
                elif sig not in self.SIGNALS:
                    logger.debug('%s, unhandled signal %d' % (self.label, sig))
                    continue
                elif sig == signal.SIGTERM:
                    raise StopIteration
                elif sig == signal.SIGHUP:
                    raise StopIteration
                elif sig == signal.SIGUSR1:
                    # todo handle restart
                    pass
                elif sig == signal.SIGUSR2:
                    # todo handle restart
                    pass

                dt = self.dt_set - (time() - t_start)
                if dt > 0:
                    sleep(dt)
        except StopIteration:
            self.stop()
            sys.exit(0)
        except:
            logger.debug('%s, unhandled exception\n%s' % (self.label, traceback.format_exc()))
            sys.exit(0)

    def loop(self):
        """
        override this
        """
        return 1, None

    def cleanup(self):
        """
        override this
        """
        pass

    def signal(self, signum=None, frame=None):
        """
        receive signals
        """
        self.SIG_QUEUE.append(signum)

    def stop(self, signum=None, frame=None):
        """
        handel's a termination signal
        """
        BackgroundProcess.objects.filter(pk=self.process_id
                                         ).update(pid=0, last_update=datetime_now(), message='stopping..')
        # run the cleanup
        self.cleanup()
        BackgroundProcess.objects.filter(pk=self.process_id).update(pid=0,
                                                                    last_update=datetime_now(),
                                                                    message='stopped')


class SingleDeviceDAQProcess(Process):
    def __init__(self, dt=5, **kwargs):
        self.last_query = 0
        self.dt_query_data = 0
        self.device = None
        self.device_id = None
        super(SingleDeviceDAQProcess, self).__init__(dt=dt, **kwargs)

    def init_process(self):
        """
        init a standard daq process for a single device
        """
        self.device = Device.objects.filter(protocol__daq_daemon=1, active=1, id=self.device_id).first()
        if not self.device:
            return False
        self.dt_set = min(self.dt_set, self.device.polling_interval)
        self.dt_query_data = self.device.polling_interval
        try:
            self.device = self.device.get_device_instance()
        except:
            var = traceback.format_exc()
            logger.error("exception while initialisation of DAQ Process for Device %d %s %s" % (
                self.device_id, linesep, var))

        return True

    def loop(self):

        # process write tasks
        for task in DeviceWriteTask.objects.filter(done=False, start__lte=time(), failed=False,
                                                   variable__device_id=self.device_id):
            if task.variable.scaling is not None:
                task.value = task.variable.scaling.scale_output_value(task.value)
            if self.device.write_data(task.variable.id, task.value):
                task.done = True
                task.finished = time()
                task.save()
            else:
                task.failed = True
                task.finished = time()
                task.save()
        if time() - self.last_query > self.dt_query_data:
            self.last_query = time()
            # Query data
            tmp_data = self.device.request_data()
            if isinstance(tmp_data, list):
                if len(tmp_data) > 0:
                    return 1, [tmp_data, ]

        return 1, None

    def cleanup(self):
        """
        mark the process as done
        """
        BackgroundProcess.objects.filter(pk=self.process_id).delete()


class MultiDeviceDAQProcess(Process):
    def __init__(self, dt=5, **kwargs):
        self.device_ids = []
        self.devices = {}
        self.dt_query_data = 3600.0
        self.last_query = 0
        super(MultiDeviceDAQProcess, self).__init__(dt=dt, **kwargs)

    def init_process(self):
        """
        init a standard daq process for multiple devices
        """

        for item in Device.objects.filter(protocol__daq_daemon=1, active=1, id__in=self.device_ids):
            try:
                tmp_device = item.get_device_instance()
                if tmp_device is not None:
                    self.devices[item.pk] = tmp_device
                    self.dt_set = min(self.dt_set, item.polling_interval)
                    self.dt_query_data = min(self.dt_query_data, item.polling_interval)
            except:
                var = traceback.format_exc()
                logger.error("exception while initialisation of DAQ Process for Device %d %s %s" % (
                    item.pk, linesep, var))

        return True

    def loop(self):
        data = [[]]
        for device_id, device in self.devices.items():
            # process write tasks
            for task in DeviceWriteTask.objects.filter(done=False, start__lte=time(),
                                                       failed=False, variable__device_id=device_id):
                if task.variable.scaling is not None:
                    task.value = task.variable.scaling.scale_output_value(task.value)
                if device.write_data(task.variable.id, task.value):
                    task.done = True
                    task.finished = time()
                    task.save()
                else:
                    task.failed = True
                    task.finished = time()
                    task.save()
        if time() - self.last_query > self.dt_query_data:
            self.last_query = time()
            for device_id, device in self.devices.items():
                # Query data
                tmp_data = device.request_data()
                if isinstance(tmp_data, list):
                    if len(tmp_data) > 0:
                        if len(data[-1]) + len(tmp_data) < 998:
                            # add to the last write job
                            data[-1] += tmp_data
                        else:
                            # add to next write job
                            data.append(tmp_data)
            return 1, data
        else:
            return 1, None

    def cleanup(self):
        """
        mark the process as done
        """
        BackgroundProcess.objects.filter(pk=self.process_id).delete()
