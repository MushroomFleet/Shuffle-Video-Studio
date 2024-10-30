@echo off
echo Starting Shuffle Joiner...

:: Activate virtual environment
echo Activating virtual environment...
call .\venv\Scripts\activate

if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

:: Run the joiner script
echo Running Shuffle Joiner...
python ShuffleJoiner.py

pause
