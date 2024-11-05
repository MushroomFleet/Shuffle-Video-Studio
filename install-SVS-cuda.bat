@echo off
echo Starting installation process...

:: Check if Python is installed
python --version > nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.6 or higher from python.org
    pause
    exit /b 1
)

echo Creating virtual environment...
python -m venv venv

echo Activating virtual environment...
call .\venv\Scripts\activate

if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing PyTorch with CUDA support...
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

echo Installing audio processing dependencies...
pip install librosa
pip install soundfile

echo Installing other required packages...
pip install numpy
pip install moviepy
pip install decorator
pip install proglog
pip install tqdm
pip install requests
pip install av
pip install psutil

echo Checking CUDA availability...
python -c "import torch; print('CUDA Available:', torch.cuda.is_available()); print('CUDA Device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None')"

echo Testing audio processing libraries...
python -c "import librosa; import soundfile; print('Audio processing libraries installed successfully!')"

echo Installation complete!
echo.
echo You can now run the video processing scripts with GPU acceleration
echo and beat synchronization features.
echo.
echo Available scripts:
echo - run-splitter.bat: Regular video splitting
echo - run-splitter-CUDA.bat: GPU-accelerated video splitting
echo - run-beat-splitter-cuda.bat: Beat-synchronized video splitting
echo - run-shuffle.bat: Clip shuffling
echo - run-joiner.bat: Clip joining
echo.
pause