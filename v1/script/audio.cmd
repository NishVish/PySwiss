@echo off
REM Restart Windows Audio service
net stop Audiosrv
net start Audiosrv
