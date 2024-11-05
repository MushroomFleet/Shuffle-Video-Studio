@echo off
echo Activating virtual environment...
call .\venv\Scripts\activate

echo Starting Beat-Synchronized CUDA Video Splitter...
python beat-splitter-cuda.py

pause
