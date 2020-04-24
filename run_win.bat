@echo off
echo Python TLS Multiclient Server v1.0
echo emerson.goulart@lifemed.com.br
echo Running...

rem IP get
rem for /f "delims=[] tokens=2" %%a in ('ping -4 -n 1 %ComputerName% ^| findstr [') do rem set NetworkIP=%%a
rem echo Network IP: %NetworkIP%

set ip=%1
set row=%2
set col=%3

set /a x=0
set /a y=0
set /a i=0

rem set /a size=%row% * %col%
rem echo %size%

for /L %%r in (1,1,%row%) do call :calc_y %%r
goto :eof

:calc_y
set /a temp=%1
set /a y=((%temp% - 1) * 220) + 20
rem echo %y%

for /L %%c in (1,1,%col%) do call :calc_x %%c
set /a x=0
goto :eof

:calc_x
set /a temp=%1
set /a i=%i% + 1
set /a x=((%temp% - 1) * 328) + 20
rem echo %x%
rem echo %i%

start python wxform.py %i% %ip% %x% %y%

rem goto :eof

  




