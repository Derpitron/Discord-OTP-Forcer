@echo off
echo Installing requirements...
pip install -r "%~dp0..\..\requirements.txt"
echo Requirements installed!

start notepad.exe "%~dp0..\..\user\cfg.yml"
echo Setup the account and program details here.

:LOOP
tasklist | find /i "notepad.exe" > nul
if errorlevel 1 goto ENDLOOP
ping -n 1 -w 1000 127.0.0.1 > nul
goto LOOP

:ENDLOOP
pause