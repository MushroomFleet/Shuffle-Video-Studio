@echo off
echo Starting Video Shuffle Studio WebUI...

:: Activate virtual environment
echo Activating virtual environment...
call .\venv\Scripts\activate

if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

:: Run the WebUI script
echo Running WebUI...
python webui.py

pause