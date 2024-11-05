@echo off
echo Starting Beat Shuffle Joiner...

:: Activate virtual environment
echo Activating virtual environment...
call .\venv\Scripts\activate

if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

:: Run the beat joiner script
echo Running Beat Shuffle Joiner...
python beat-shuffle-joiner.py

pause
