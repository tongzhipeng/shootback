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

from slaver import main_slaver
import threading
from configparser import ConfigParser
from pathlib import Path

cur_exe_dir = Path(sys.argv[0]).parent
slaver_logger = logging.getLogger()


def init_log():
    global slaver_logger
    slaver_logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(cur_exe_dir.joinpath('master.log'))
    slaver_logger.addHandler(file_handler)


class SlaverService(win32serviceutil.ServiceFramework):
    # 服务名
    _svc_name_ = "SlaverService"
    # 服务在windows系统中显示的名称
    _svc_display_name_ = "Python Service Test"
    # 服务的描述
    _svc_description_ = "This code is a Python service Test"
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
        SlaverService.config.read(cur_exe_dir.joinpath('slaver.ini'))
        self.log('SlaverService.__init__')
        try:
            slaver_logger.info('args=%s', args)
        except BaseException as e:
            self.log('init exception=' + str(e))

    def ReportServiceStatus(self, serviceStatus, waitHint=5000, win32ExitCode=0, svcExitCode=0):
        slaver_logger.info('ReportServiceStatus status=%d', serviceStatus)
        if not self.debug:
            super(MasterService, self).ReportServiceStatus(serviceStatus, waitHint, win32ExitCode, svcExitCode)


    def SvcDoRun(self):
        # 把自己的代码放到这里，就OK
        # 等待服务被停止
        slaver_logger.info('python service SvcDoRun...')
        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
        try:
            raw_args = SlaverService.config.get('slaver', 'raw_args', fallback='-m ipisshit.com:8082 -t 127.0.0.1:3389')
            log_file = cur_exe_dir.joinpath('slaver.log')
            slaver_thread = threading.Thread(target=main_slaver, args=(raw_args.split(), log_file))
            slaver_thread.start()
        
            self.ReportServiceStatus(win32service.SERVICE_RUNNING)
            self.log('start')
            while self.working_:
                try:
                    slaver_logger.info('SvcDoRun looping...')
                except BaseException as e:
                    self.log('SvcDoRun exception=' + str(e) + ':' + traceback.format_exc())
                # logger.info("SvcDoRun looping...")
                time.sleep(3)
            # win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)
            self.log('done')
        except BaseException as e:
            error_log = 'Exception : %s' % e
            self.log(error_log)
            self.SvcStop()

    def log(self, msg):
        servicemanager.LogInfoMsg(str(msg))
        slaver_logger.error(msg)

    def SvcStop(self):
        # 先告诉SCM停止这个过程
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        # 设置事件
        # win32event.SetEvent(self.hWaitStop)
        self.working_ = False


if __name__ == '__main__':
    init_log()
    slaver_logger.info('master service start...')
    if len(sys.argv) > 1 and sys.argv[1] == 'debug':
        service = SlaverService('Debug')
        service.SvcDoRun()
        exit(0)

    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(SlaverService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(SlaverService)
    # 括号里参数可以改成其他名字，但是必须与class类名一致；
