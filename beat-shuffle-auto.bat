@echo off
echo Starting Beat-Synchronized Auto Shuffle...

:: Activate virtual environment
echo Activating virtual environment...
call .\venv\Scripts\activate

if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

:: Run the beat shuffle script
echo Running Beat-Synchronized Auto Shuffle...
python beat-shuffle-auto.py

pause
