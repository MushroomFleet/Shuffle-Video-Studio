@echo off
echo Starting requirements update...

:: Activate virtual environment
echo Activating virtual environment...
call .\venv\Scripts\activate

if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

:: Install requirements
echo Installing requirements from requirements.txt...
pip install -r requirements.txt

echo.
echo Requirements update complete!
echo.
pause
