@echo off
echo Updating dependencies...
python.exe -m pip install --upgrade -r "%~dp0..\..\dependencies.txt"
echo Dependencies updated!
pause
