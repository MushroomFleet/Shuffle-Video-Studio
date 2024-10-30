@echo off
echo Starting Shuffle Splits...

:: Activate virtual environment
echo Activating virtual environment...
call .\venv\Scripts\activate

if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

:: Run the shuffle script
echo Running Shuffle Splits v2...
python shuffle-splits-v2.py

pause
