@cd /d %~dp0%
@echo install...
@SlaverService.exe --startup auto install
@echo install service finish!
@echo start...
@SlaverService.exe start
@echo start finish!
@pause