@echo off
echo Activating virtual environment...
call .\venv\Scripts\activate

echo Starting Bar-Synchronized CUDA Video Splitter v2...
python beat-splitter-cudaV2.py

pause
