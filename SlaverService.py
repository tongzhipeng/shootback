#!/usr/bin/env python
#encoding: utf-8

import win32serviceutil
import win32service
import win32event
import sys, os
import servicemanager
import time
#import multiprocessing
import win32timezone
import logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

class SlaverService(win32serviceutil.ServiceFramework):
    # 服务名
    _svc_name_ = "SlaverService"
    # 服务在windows系统中显示的名称
    _svc_display_name_ = "Python Service Test"
    # 服务的描述
    _svc_description_ = "This code is a Python service Test"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.working_ = True

    def SvcDoRun(self):
        # 把自己的代码放到这里，就OK
        # 等待服务被停止
        print('python service SvcDoRun...')
        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
        try:
            self.ReportServiceStatus(win32service.SERVICE_RUNNING)
            self.log('start')
            self.log('wait')
            while self.working_:
                logger.info("SvcDoRun looping...")
                time.sleep(3)
            #win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)
            self.log('done')
        except BaseException as e:
            self.log('Exception : %s' % e)
            self.SvcStop()

    def log(self, msg):
        servicemanager.LogInfoMsg(str(msg))

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
#         servicemanager.PrepareToHostSingle(SlaverService)
#         servicemanager.Initialize('SlaverService', evtsrc_dll)
#         servicemanager.StartServiceCtrlDispatcher()
#     else:
#         win32serviceutil.HandleCommandLine(SlaverService)
#     # 括号里参数可以改成其他名字，但是必须与class类名一致；

if __name__ == '__main__':
    #multiprocessing.freeze_support()
    print('hello start...')
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(SlaverService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(SlaverService)
    # 括号里参数可以改成其他名字，但是必须与class类名一致；
