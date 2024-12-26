# Video Shuffle Studio
![Demo UI](https://raw.githubusercontent.com/MushroomFleet/Shuffle-Video-Studio/main/images/SVS-webUI.png)

A suite of tools for splitting, shuffling, and rejoining video clips with both CPU and GPU-accelerated options. Now includes a user-friendly Web Interface.

- Full Video Explainer: https://www.youtube.com/watch?v=z1JfE5iRh44 (Walkthrough)
- Sony pc110e-pal Output: https://www.youtube.com/watch?v=ElKTb3J2OkI
- Sony dcr-trv310 Output: https://www.youtube.com/watch?v=4XrAMXHPjBM
- AI Gen Video Output: https://www.youtube.com/watch?v=4CXV-lMXy7c (Mochi1 Preview)
- (music added in post, central frame is the output)
- Helldivers2 with AI Music https://www.youtube.com/watch?v=uTzoe-NEbzk

## Recent Updates
- December 26th '24: Added Gradio-based Web Interface for easier operation
- November 1st '24: Added script to convert Mochi video outputs from ComfyUI into the format SVS Splitter creates
- Beat-synchronized splitting and joining now available in both CLI and Web Interface

## Setup Instructions

### Prerequisites
- Python 3.6 or higher
- NVIDIA GPU with CUDA support (for CUDA-enabled versions)
- FFmpeg installed and in system PATH

### Initial Setup
1. Clone or download this repository
2. Run `install-SVS-cuda.bat` to create virtual environment and install all requirements
3. Run `update-requirements.bat` if you need to update dependencies later

## Using the Web Interface

### Starting the Web UI
1. Run `run-webui.bat` to start the Web Interface
2. Once started, open your browser to `http://127.0.0.1:7860`
3. The interface shows available GPU and processing options

### Web Interface Features

#### Standard Split Tab
- Upload video files directly through the interface
- Set custom clip duration in seconds
- Automatic output to organized folders
- GPU-accelerated processing

#### Beat Split Tab
- Upload both video and audio files
- Choose number of bars per segment
- Synchronize video splits with musical beats
- Automatic beat detection and tempo analysis

#### Shuffle Tab
- Enter input folder path for split clips
- Choose between simple or size-reward shuffle
- Adjust reward percentage for size-based shuffling
- Get organized output with timestamp-based folders

#### Join Tab
- Enter folder path containing clips to join
- Automatic clip ordering and concatenation
- Progress tracking and error reporting

#### Beat Join Tab
- Combine video clips with background music
- Upload custom audio tracks
- Automatic audio sync and length adjustment

### Output Organization
- All processed files are saved in the "output" directory
- Each operation creates a timestamped subfolder
- Temporary files handled automatically
- Original files preserved

## Command Line Tools

All original command-line tools remain available for advanced users:

### 1. Video Splitters
- `run-splitter.bat` - CPU-based processing
- `run-splitter-CUDA.bat` - GPU-accelerated processing

### 2. Clip Shufflers
- `run-shuffle.bat` - Access both shuffle methods

### 3. Clip Joiners
- `run-joiner.bat` - Standard joining
- `beat-joiner.bat` - Music-synchronized joining

## File Structure
```
video-shuffle-studio/
├── install-SVS-cuda.bat
├── update-requirements.bat
├── requirements.txt
├── run-webui.bat           # New WebUI launcher
├── webui.py               # New WebUI implementation
├── video-splitter-v3.py
├── video-splitter-cuda.py
├── shuffle-splits-v2.py
├── ShuffleJoiner.py
├── run-splitter.bat
├── run-splitter-CUDA.bat
├── run-shuffle.bat
├── run-joiner.bat
└── output/                # Organized output directory
    └── [timestamped folders]
```

## Performance Notes
- CUDA versions require NVIDIA GPU with appropriate drivers
- WebUI shows available GPU and processing capabilities
- Size Reward shuffle analyzes compression ratios
- Processing speed depends on:
  - Video resolution
  - Clip duration
  - Available RAM
  - GPU capabilities (for CUDA versions)

## Troubleshooting

### Web Interface Issues
1. If the interface fails to load:
   - Check if Python and dependencies are properly installed
   - Verify port 7860 is not in use
   - Check terminal for error messages

2. If file processing fails:
   - Ensure input files are valid video/audio formats
   - Check available disk space
   - Verify GPU drivers are up to date

### General Issues
1. If virtual environment fails to activate:
   - Delete 'venv' folder
   - Run install-SVS-cuda.bat again

2. If CUDA versions fail:
   - Verify NVIDIA GPU presence
   - Update GPU drivers
   - Use standard versions instead

3. If joins are incomplete:
   - Check available disk space
   - Verify all clips are valid MP4 files

## System Requirements
- Windows 10 or higher
- Python 3.6+
- 8GB RAM minimum (16GB recommended)
- For CUDA versions:
  - NVIDIA GPU
  - CUDA Toolkit 11.8 or higher
  - Latest NVIDIA drivers

## License
Open source - feel free to modify and distribute.
