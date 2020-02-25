@echo off
setlocal

rem if another tool opens the file (e.g. the comparison tool), the copy command does not work 
copy /Y "..\androidApp\app\google-services.json" "google-services.json"

IF %ERRORLEVEL% NEQ 0 (
  ECHO Error - copy returned errorlevel %ERRORLEVEL%
  GOTO :someError 
)

:success
endlocal
@echo on
exit

:someError
pause
endlocal
@echo on
exit






