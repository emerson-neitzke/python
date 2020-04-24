@echo off
set /a var1=0
set /a var2=0

for /f "delims=[] tokens=2" %%a in ('ping -4 -n 1 %ComputerName% ^| findstr [') do set NetworkIP=%%a
echo Network IP: %NetworkIP%

FOR /L %%X IN (1,1,11) DO call :body %%X
goto :eof

:body
set var1=%1
echo %var1%
goto :eof