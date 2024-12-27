# Video Shuffle Studio
![Demo UI](https://raw.githubusercontent.com/MushroomFleet/Shuffle-Video-Studio/main/images/SVS-webUI.png)

A suite of tools for splitting, shuffling, and rejoining video clips with both CPU and GPU-accelerated options. Features a user-friendly Web Interface and advanced color-based sorting capabilities.

## Recent Updates
- December 27th '24: Added color-based shuffle modes (similarity and transitions)
- December 26th '24: Added Gradio-based Web Interface for easier operation
- November 1st '24: Added script to convert Mochi video outputs from ComfyUI
- Added beat-synchronized splitting and joining in both CLI and Web Interface

## Features

### Video Processing
- GPU-accelerated video splitting (CUDA support)
- Beat-synchronized splitting with audio analysis
- Multiple shuffle modes:
  - Simple random shuffle
  - Size-based reward shuffle
  - Color similarity shuffle
  - Color transition effects
- Video joining with optional audio synchronization

### Color-Based Shuffling
1. **Color Similarity Mode**
   - Groups clips with similar color palettes
   - Creates visually cohesive sequences
   - Ideal for aesthetic arrangements

2. **Color Transition Effects**
   - Rainbow: Full spectrum color progression
   - Sunset: Warm orange to cool purple transition
   - Ocean: Light to deep blue progression
   - Creates smooth visual narratives

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
2. Open your browser to `http://127.0.0.1:7860`
3. Interface shows available GPU and processing options

### Web Interface Features

#### Standard Split Tab
- Upload video files directly
- Set custom clip duration in seconds
- Automatic output to organized folders
- GPU-accelerated processing

#### Beat Split Tab
- Upload both video and audio files
- Choose number of bars per segment
- Synchronize video splits with musical beats
- Automatic beat detection and tempo analysis

#### Shuffle Tab
1. **Simple Shuffle**
   - Basic random shuffle with hex-based naming
   - Fast and memory-efficient

2. **Size Reward Shuffle**
   - Analyzes file sizes for quality estimation
   - Keeps specified percentage of larger files
   - Best for quality-based selection

3. **Color Shuffle Modes**
   - Similarity Mode: Groups visually similar clips
   - Transition Mode: Creates color flow effects
   - Choose from Rainbow, Sunset, or Ocean transitions
   - Color analysis with automatic dominant color detection

#### Join Tab
- Enter folder path containing clips to join
- Automatic clip ordering and concatenation
- Progress tracking and error reporting

#### Beat Join Tab
- Combine video clips with background music
- Upload custom audio tracks
- Automatic audio sync and length adjustment

## Command Line Tools

All tools are available via command line for advanced users or automation:

### 1. Video Splitters
- `run-splitter.bat` - CPU-based processing
- `run-splitter-CUDA.bat` - GPU-accelerated processing
- `run-splitter-cuda-v2.bat` - Bar-synchronized splitting

### 2. Clip Shufflers
- `run-shuffle.bat` - Access all shuffle methods:
  - Simple random shuffle
  - Size-reward shuffle
  - Color-based shuffling (similarity/transitions)

### 3. Clip Joiners
- `run-joiner.bat` - Standard joining
- `beat-joiner.bat` - Music-synchronized joining

## Output Organization
- All processed files saved in "output" directory
- Each operation creates timestamped subfolder
- Automatic temp file cleanup
- Original files preserved

## Performance Notes
- CUDA versions require NVIDIA GPU with appropriate drivers
- Color analysis optimized for memory efficiency
- Processing speed depends on:
  - Video resolution
  - Clip duration
  - Available RAM
  - GPU capabilities (for CUDA versions)
  - Color analysis settings

## Troubleshooting

### Common Issues

1. **Web Interface Issues**
   - Check if Python and dependencies are installed
   - Verify port 7860 is not in use
   - Check terminal for error messages

2. **Color Analysis Issues**
   - Ensure enough disk space for processing
   - Check video file integrity
   - Verify clip format compatibility

3. **CUDA Processing Issues**
   - Verify NVIDIA GPU presence
   - Update GPU drivers
   - Use standard versions if CUDA unavailable

### General Solutions
1. If virtual environment fails:
   - Delete 'venv' folder
   - Run install-SVS-cuda.bat again

2. If color analysis is slow:
   - Reduce number of sample frames
   - Use smaller clip sizes
   - Check available memory

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

## Support
If you encounter issues or need help:
1. Check the error messages in the terminal
2. Verify your file naming patterns
3. Ensure Python is properly installed
4. Check disk space and permissions

## License
Open source - feel free to modify and distribute.
