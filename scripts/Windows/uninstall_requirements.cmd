@echo off
echo Uninstalling requirements...
python.exe -m pip uninstall -r "%~dp0..\..\requirements.txt" -y
echo Requirements uninstalled!
pause
