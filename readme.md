# Video Shuffle Studio

A suite of tools for splitting, shuffling, and rejoining video clips with both CPU and GPU-accelerated options, now featuring beat-synchronized video processing.

- Full Video Explainer: https://www.youtube.com/watch?v=z1JfE5iRh44 (Walkthrough)
- Sony pc110e-pal Output: https://www.youtube.com/watch?v=ElKTb3J2OkI
- Sony dcr-trv310 Output: https://www.youtube.com/watch?v=4XrAMXHPjBM
- AI Gen Video Output: https://www.youtube.com/watch?v=4CXV-lMXy7c (Mochi1 Preview)
- (music added in post, central frame is the output)

## update 2
- November 5th '24: Added Beat Synchronization Suite
  - Bar-synchronized video splitting with CUDA acceleration
  - Automatic beat-based shuffling with audio duration matching
  - Audio-synchronized video joining
  - Support for custom bar lengths and time signatures

## update 1
- November 1st '24: Added script to convert Mochi video outputs from ComfyUI into the format SVS Splitter creates
- This allows AI output videos (of the same dimensions) to be shuffled and joined with SVS studio.
- https://github.com/MushroomFleet/Shuffle-Video-Studio/blob/main/Comfy-Convert/comfyoutput-2-splits.md

## Setup Instructions

### Prerequisites
- Python 3.6 or higher
- NVIDIA GPU with CUDA support (for CUDA-enabled versions)
- FFmpeg installed and in system PATH
- Audio processing capabilities require:
  - librosa
  - soundfile

### Initial Setup
1. Clone or download this repository
2. Run `install-SVS-cuda.bat` to create virtual environment and install all requirements including CUDA support
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

#### Beat-Synchronized CUDA Version (beat-splitter-cudaV2.py)
- GPU-accelerated video splitting synchronized to musical bars
- Automatic tempo and beat detection
- Run using: `run-splitter-cuda-v2.bat`

Features:
- Customizable bars per segment (1, 2, 4, or 8 bars)
- Automatic tempo detection
- Beat and bar analysis
- Progress tracking
- Memory optimization
- Creates named output folders

### 2. Clip Shufflers

#### Standard Shuffler (shuffle-splits-v2.py)
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

#### Beat-Synchronized Auto Shuffler (beat-shuffle-auto.py)
Run using: `beat-shuffle-auto.bat`

Features:
- Automatic calculation of optimal clip selection based on audio duration
- Size-based analysis for high-action content
- Synchronizes output length with audio track
- Progress tracking and memory optimization

### 3. Clip Joiners

#### Standard Version (ShuffleJoiner.py)
- Joins shuffled clips back into single video
- CPU-based processing
- Run using: `run-joiner.bat`

#### Beat-Synchronized Joiner (beat-shuffle-joiner.py)
- Joins clips and synchronizes with music track
- Run using: `beat-joiner.bat`

Features:
- Audio track integration
- Automatic audio length matching
- Progress tracking
- Error handling
- Maintains video quality

## Workflow Examples

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
5. Run joiner:
   ```
   run-joiner.bat
   ```

### Beat-Synchronized Workflow:
1. Place your source video and audio files in the project directory
2. Run beat-synchronized splitter:
   ```
   run-splitter-cuda-v2.bat
   ```
   - Enter video filename
   - Enter audio filename
   - Select bars per segment (1-8 bars)

3. Run beat-synchronized auto shuffler:
   ```
   beat-shuffle-auto.bat
   ```
   - Enter audio file path
   - Enter input folder path
   - Enter output folder name

4. Run beat-synchronized joiner:
   ```
   beat-joiner.bat
   ```
   - Enter audio file path
   - Enter folder containing shuffled clips
   - Final video will be saved in "beat-output" folder

## File Structure
```
video-shuffle-studio/
├── install-SVS-cuda.bat
├── update-requirements.bat
├── requirements.txt
├── video-splitter-v3.py
├── video-splitter-cuda.py
├── beat-splitter-cudaV2.py
├── shuffle-splits-v2.py
├── beat-shuffle-auto.py
├── ShuffleJoiner.py
├── beat-shuffle-joiner.py
├── run-splitter.bat
├── run-splitter-CUDA.bat
├── run-splitter-cuda-v2.bat
├── run-shuffle.bat
├── beat-shuffle-auto.bat
├── run-joiner.bat
└── beat-joiner.bat
```

## Performance Notes
- CUDA versions require NVIDIA GPU with appropriate drivers
- Beat synchronization requires additional CPU resources for audio analysis
- Size Reward shuffle analyzes compression ratios
- Processing speed depends on:
  - Video resolution
  - Clip duration/bar length
  - Available RAM
  - GPU capabilities (for CUDA versions)
  - Audio analysis complexity

## Beat Synchronization Notes
- Audio files should be high-quality MP3 or WAV format
- Supports various time signatures (defaults to 4/4)
- Bar detection works best with clear rhythmic content
- Options for 1, 2, 4, or 8 bars per segment
- Auto-shuffler matches final video length to audio duration

## Troubleshooting
1. If virtual environment fails to activate:
   - Delete 'venv' folder
   - Run install-SVS-cuda.bat again

2. If CUDA versions fail:
   - Verify NVIDIA GPU presence
   - Update GPU drivers
   - Use standard versions instead

3. If beat detection is inaccurate:
   - Use high-quality audio files
   - Try audio with clear beat patterns
   - Verify audio file format (MP3/WAV)

4. If joins are incomplete:
   - Check available disk space
   - Verify all clips are valid MP4 files
   - Check audio file compatibility

## System Requirements
- Windows 10 or higher
- Python 3.6+
- 8GB RAM minimum (16GB recommended)
- For CUDA versions:
  - NVIDIA GPU
  - CUDA Toolkit 11.8 or higher
  - Latest NVIDIA drivers
- For beat synchronization:
  - Additional 2GB RAM recommended
  - High-quality audio source files

## License
Open source - feel free to modify and distribute.
