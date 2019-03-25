@cd /d %~dp0%
@echo stoping...
@SlaverService.exe stop
@echo stoped!
@echo uninstalling service..
@SlaverService.exe remove
@echo unistall finish!
@pause
