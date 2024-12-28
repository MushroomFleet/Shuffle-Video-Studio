@echo off
echo Starting Video Shuffle Studio WebUI...

:: Activate virtual environment
echo Activating virtual environment...
call .\venv\Scripts\activate

if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    echo Please run install-SVS-cuda.bat if you haven't already.
    pause
    exit /b 1
)

:: Check for required modules
echo Checking WebUI modules...
for %%F in (
    webui_main.py
    webui_studio.py
    webui_split_tab.py
    webui_beat_tab.py
    webui_shuffle_tab.py
    webui_join_tab.py
    webui_beat_join_tab.py
    webui_utils.py
) do (
    if not exist "%%F" (
        echo ERROR: Missing required module %%F
        pause
        exit /b 1
    )
)

:: Run the WebUI script
echo Launching WebUI...
python webui_main.py

if errorlevel 1 (
    echo ERROR: WebUI encountered an error
    pause
    exit /b 1
)

pause