@echo off
echo Activating virtual environment...
call .\venv\Scripts\activate

echo Starting CUDA Video Splitter...
python video-splitter-cuda.py

pause
