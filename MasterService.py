#!/usr/bin/env python
# - encoding: utf-8

import win32serviceutil
import win32service
import win32event
import sys
import servicemanager
import time
import win32timezone
import logging
import traceback

from master import main_master
import threading
from configparser import ConfigParser
from pathlib import Path

cur_exe_dir = Path(sys.argv[0]).parent
master_logger = logging.getLogger()


def init_log():
    global master_logger
    master_logger.setLevel(logging.DEBUG)
    fileHandler = logging.FileHandler(cur_exe_dir.joinpath('master.log'))
    # master_logger.addHandler(fileHandler)

class MasterService(win32serviceutil.ServiceFramework):
    # 服务名
    _svc_name_ = "MasterService"
    # 服务在windows系统中显示的名称
    _svc_display_name_ = "MasterService"
    # 服务的描述
    _svc_description_ = "This code is a shootback MasterService"
    config = ConfigParser()
    def __init__(self, args):
        print('init...')
        if args != 'Debug':
            self.debug = False
        else:
            self.debug = True
        if not self.debug:
            win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.working_ = True
        self.args = args
        MasterService.config.read(cur_exe_dir.joinpath('master.ini'))
        self.log('MasterService.__init__')
        try:
            master_logger.info('args=%s', args)
        except BaseException as e:
            self.log('init exception=' + str(e))

    def ReportServiceStatus(self, serviceStatus, waitHint = 5000, win32ExitCode = 0, svcExitCode = 0):
        master_logger.info('ReportServiceStatus status=%d', serviceStatus)
        if not self.debug:
            super(MasterService, self).ReportServiceStatus(serviceStatus, waitHint, win32ExitCode, svcExitCode)

    def SvcDoRun(self):
        # 把自己的代码放到这里，就OK
        # 等待服务被停止
        master_logger.info('python service SvcDoRun...')
        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
        try:
            raw_args = MasterService.config.get('master', 'raw_args', fallback='-m 0.0.0.0:8082 -c 0.0.0.0:3390')
            log_fille = cur_exe_dir.joinpath('master.log')
            print('')
            master_thread = threading.Thread(target=main_master, args=(raw_args.split(), log_fille))
            master_thread.start()

            self.ReportServiceStatus(win32service.SERVICE_RUNNING)
            self.log('start')
            while self.working_:
                try:
                    master_logger.info('SvcDoRun looping...')
                except BaseException as e:
                    self.log('SvcDoRun exception=' + str(e) + ':' + traceback.format_exc())
                # logger.info("SvcDoRun looping...")
                time.sleep(3)
            #win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)
            self.log('done')
        except BaseException as e:
            error_log = 'Exception : %s' % e
            self.log(error_log)
            self.SvcStop()

    def log(self, msg):
        servicemanager.LogInfoMsg(str(msg))
        master_logger.error(msg)

    def SvcStop(self):
        # 先告诉SCM停止这个过程
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        # 设置事件
        #win32event.SetEvent(self.hWaitStop)
        self.working_ = False

# if __name__ == '__main__':
#     #multiprocessing.freeze_support()
#     if len(sys.argv) == 1:
#         evtsrc_dll = os.path.abspath(servicemanager.__file__)
#         servicemanager.PrepareToHostSingle(MasterService)
#         servicemanager.Initialize('MasterService', evtsrc_dll)
#         servicemanager.StartServiceCtrlDispatcher()
#     else:
#         win32serviceutil.HandleCommandLine(MasterService)
#     # 括号里参数可以改成其他名字，但是必须与class类名一致；

if __name__ == '__main__':
    init_log()
    #multiprocessing.freeze_support()
    master_logger.info('master service start...')
    if len(sys.argv) > 1 and  sys.argv[1] == 'debug':
        service = MasterService('Debug')
        service.SvcDoRun()
        exit(0)

    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(MasterService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(MasterService)
    # 括号里参数可以改成其他名字，但是必须与class类名一致；
