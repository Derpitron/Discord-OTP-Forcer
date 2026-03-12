@echo off
echo Uninstalling requirements...
pip uninstall -r "%~dp0..\..\requirements.txt" -y
echo Requirements uninstalled!
pause
