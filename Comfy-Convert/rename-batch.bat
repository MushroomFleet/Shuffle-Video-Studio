@echo off
cls
echo File Renaming Utility
echo ====================
echo.
echo This script will rename files from [prefix]_00000.mp4 format to clip_0000.mp4 format
echo.

REM Check if Python is installed
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH!
    echo Please install Python and try again.
    pause
    exit /b 1
)

:ask_prefix
set /p prefix="Enter the prefix word of your files (e.g., donut): "
if "%prefix%"=="" (
    echo Please enter a valid prefix word.
    goto ask_prefix
)

echo.
echo Looking for files starting with: %prefix%_00000.mp4
echo Will rename them to format: clip_0000.mp4
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause >nul

REM Run the Python script with the prefix as an argument
python rename_files.py "%prefix%"

echo.
echo Process completed.
pause
