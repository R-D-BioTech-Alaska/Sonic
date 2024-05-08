@echo off
cls
echo Checking for Python installation...
where python > nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Python is not installed. Please install Python and try again.
    pause
    exit /b
)

echo Python is installed.
echo Setting up the environment...

python -m pip install PyQt5 numpy pyaudio --user

echo Starting the application...
start "" "Sonic.pyw"
echo Exiting setup.
pause
exit
