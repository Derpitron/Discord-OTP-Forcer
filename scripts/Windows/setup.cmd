@echo off

set program_saved=0
set account_saved=0

for %%A in ("%~dp0..\..\config\program.yml") do set program_timestamp=%%~tA
for %%A in ("%~dp0..\..\config\account.yml") do set account_timestamp=%%~tA

echo Installing requirements...
python.exe -m pip install -r "%~dp0..\..\requirements.txt"
echo Requirements installed!

echo Set the program settings (program.yml) and your account details (account.yml) in the Notepad windows that have just opened
timeout /t 1 >nul
start notepad.exe "%~dp0..\..\config\program.yml"
start notepad.exe "%~dp0..\..\config\account.yml"

:LOOP
for %%A in ("%~dp0..\..\config\program.yml") do if not "%%~tA"=="%program_timestamp%" set program_saved=1
for %%A in ("%~dp0..\..\config\account.yml") do if not "%%~tA"=="%account_timestamp%" set account_saved=1

if "%program_saved%"=="1" if "%account_saved%"=="1" (
  echo Configuration files saved.
  choice /m "Start forcer session now?"

  if errorlevel 2 goto END
  if errorlevel 1 (
    start start.cmd
    exit
  )
)

timeout /t 1 >nul
goto LOOP

:END
echo -----------
echo Closing...
timeout /t 2
exit

