@echo off
echo Uninstalling dependencies...
python.exe -m pip uninstall -r "%~dp0..\..\dependencies.txt" -y
echo Dependencies uninstalled!
pause
