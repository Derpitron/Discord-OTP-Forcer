@echo off
echo Uninstalling dependencies...
python.exe -m pip uninstall -r "%~dp0..\..\requirements.txt" -y
echo Requirements dependencies!
pause
