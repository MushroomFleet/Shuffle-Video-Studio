# Video Shuffle Studio

A suite of tools for splitting, shuffling, and rejoining video clips with both CPU and GPU-accelerated options.

Full Video Explainer: https://www.youtube.com/watch?v=z1JfE5iRh44 < br/>
Example Video Output: https://www.youtube.com/watch?v=ElKTb3J2OkI
(music added in post, central frame is the output)

## Setup Instructions

### Prerequisites
- Python 3.6 or higher
- NVIDIA GPU with CUDA support (for CUDA-enabled versions)
- FFmpeg installed and in system PATH

### Initial Setup
1. Clone or download this repository
2. Run `install.bat` to create virtual environment and install basic requirements
3. Run `update-requirements.bat` if you need to update dependencies later

## Tools Overview

### 1. Video Splitters

#### Standard Version (video-splitter-v3.py)
- Splits videos into segments of specified duration
- CPU-based processing
- Run using: `run-splitter.bat`

#### CUDA Version (video-splitter-cuda.py)
- GPU-accelerated video splitting
- Requires NVIDIA GPU
- Run using: `run-splitter-CUDA.bat`

Features:
- Custom clip duration (1-3600 seconds)
- Progress tracking
- Memory usage monitoring
- Creates named output folders based on input filename

### 2. Clip Shufflers (shuffle-splits-v2.py)

Run using: `run-shuffle.bat`

Two shuffle methods available:
1. Simple Shuffle
   - Randomly renames clips using hex codes
   - Preserves original files
   - Quick and memory-efficient

2. Size Reward Shuffle
   - Analyzes file sizes to identify high-action content
   - User-defined percentage of clips to keep
   - Creates separate 'reward' folder for selected clips
   - Applies random hex names to final selection

Features:
- Custom input/output folder selection
- Progress tracking
- Memory optimization
- Detailed statistics

### 3. Clip Joiners

#### Standard Version (ShuffleJoiner.py)
- Joins shuffled clips back into single video
- CPU-based processing
- Run using: `run-joiner.bat`

Features:
- Automatic output folder creation
- Timestamp-based naming
- Progress tracking
- Error handling
- Maintains video quality

## Workflow Example

### Basic Workflow:
1. Place your source video in the project directory
2. Run splitter:
   ```
   run-splitter.bat
   # or for GPU acceleration:
   run-splitter-CUDA.bat
   ```
3. Enter video filename and desired clip duration

4. Run shuffler:
   ```
   run-shuffle.bat
   ```
   - Choose shuffle method (1 or 2)
   - Enter input folder path
   - Enter output folder name
   - For Size Reward, specify percentage to keep

5. Run joiner:
   ```
   run-joiner.bat
   ```
   - Enter folder containing shuffled clips
   - Final video will be saved in "output" folder

### CUDA Optimization
For systems with NVIDIA GPUs:
- Use CUDA version for splitting
- Expect significant performance improvements
- Automatic fallback to CPU if GPU unavailable
- Monitor GPU usage in task manager during processing

## File Structure
```
video-shuffle-studio/
├── install.bat
├── update-requirements.bat
├── requirements.txt
├── video-splitter-v3.py
├── video-splitter-cuda.py
├── shuffle-splits-v2.py
├── ShuffleJoiner.py
├── run-splitter.bat
├── run-splitter-CUDA.bat
├── run-shuffle.bat
└── run-joiner.bat
```

## Performance Notes
- CUDA versions require NVIDIA GPU with appropriate drivers
- Size Reward shuffle analyzes compression ratios
- Larger files typically indicate more action/movement
- Processing speed depends on:
  - Video resolution
  - Clip duration
  - Available RAM
  - GPU capabilities (for CUDA versions)

## Troubleshooting
1. If virtual environment fails to activate:
   - Delete 'venv' folder
   - Run install.bat again

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
