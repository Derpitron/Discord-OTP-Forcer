@echo off
echo Installing requirements...
pip install -r "%~dp0..\..\requirements.txt"
echo Requirements installed!

start notepad.exe "%~dp0..\..\config\account.yml"
echo Setup the your account details here.

start notepad.exe "%~dp0..\..\config\program.yml"
echo Setup the program configuration you want here here. 

:LOOP
tasklist | find /i "notepad.exe" > nul
if errorlevel 1 goto ENDLOOP
ping -n 1 -w 1000 127.0.0.1 > nul
goto LOOP

:ENDLOOP
pause