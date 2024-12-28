# Video Shuffle Studio
![Demo UI](https://raw.githubusercontent.com/MushroomFleet/Shuffle-Video-Studio/main/images/SVS-webUI.png)

A suite of tools for splitting, shuffling, and rejoining video clips with both CPU and GPU-accelerated options. Features a user-friendly Web Interface and advanced color-based and motion-based sorting capabilities.

## Recent Updates
- December 28th '24: Added Motion-based shuffle with Natural Eye sorting
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
  - Motion-based Natural Eye shuffle
- Video joining with optional audio synchronization

### Motion-Based Shuffling (New!)
The new Motion Analysis mode introduces sophisticated video sequence optimization using advanced motion vector analysis:

1. **Natural Eye Mode**
   - Analyzes motion patterns in each clip
   - Tracks directional movement (N, S, E, W, etc.)
   - Creates sequences that guide viewer attention naturally
   - Optimizes transitions between clips for visual flow
   - Generates detailed transition reports

2. **Analysis Settings**
   - Speed Options:
     - Fast: Quick analysis with basic motion detection
     - Balanced: Standard analysis with good accuracy
     - Precise: Detailed analysis with highest accuracy
   - Transition Control:
     - Minimum Score: Set threshold for transition quality
     - Lookahead: Control sequence optimization depth
     - Motion confidence tracking
     - Intensity matching between clips

3. **Motion Analysis Features**
   - Automatic start/end motion detection
   - Direction-based transition optimization
   - Motion intensity matching
   - Intelligent sequence optimization
   - Detailed transition reporting
   - GPU acceleration support

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

### Additional Prerequisites for Motion Analysis
The Motion Shuffle mode requires FFGLITCH to be installed and configured:
1. Download FFGLITCH from https://ffglitch.org/
2. Extract the downloaded archive to a location on your PC
3. Add the FFGLITCH directory to your system's PATH environment variable
4. Verify installation by typing "ffgac" in a command prompt - you should see the FFGLITCH help message
   
Note: FFGLITCH is only required for Motion Analysis features. All other features of Video Shuffle Studio will work without this dependency.

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

4. **Motion Shuffle Mode (New!)**
   - Analysis Speed Selection:
     - Fast: Quick analysis, suitable for simpler transitions
     - Balanced: Standard analysis with good accuracy
     - Precise: Detailed analysis, best results but slower
   - Natural Eye Mode Options:
     - Minimum Transition Score: Control transition quality (0.0-1.0)
     - Transition Lookahead: Set sequence optimization depth (1-5)
   - Features:
     - Motion pattern detection
     - Directional flow optimization
     - Transition quality scoring
     - Detailed analysis reporting

#### Join Tab
- Enter folder path containing clips to join
- Automatic clip ordering and concatenation
- Progress tracking and error reporting

#### Beat Join Tab
- Combine video clips with background music
- Upload custom audio tracks
- Automatic audio sync and length adjustment

## Using Motion Shuffle Mode

1. **Preparation**
   - Ensure clips are properly encoded
   - Higher quality clips provide better motion analysis
   - GPU recommended for faster processing

2. **Basic Steps**
   - Select "Motion" shuffle type
   - Choose analysis speed (balanced recommended for first use)
   - Adjust minimum transition score (0.5 is a good starting point)
   - Set lookahead value (3 is recommended)
   - Select input folder and start processing

3. **Understanding Output**
   - Motion analysis creates a detailed report
   - Transition scores indicate clip compatibility
   - Higher scores indicate smoother transitions
   - Review transition report for sequence details

4. **Tips for Best Results**
   - Start with "balanced" speed for testing
   - Use "precise" for final renders
   - Adjust minimum score based on results
   - Higher lookahead values create better sequences but increase processing time
   - Review transition reports to understand clip relationships

5. **Performance Notes**
   - Motion analysis is CPU/GPU intensive
   - Processing time depends on:
     - Number of clips
     - Clip duration
     - Analysis speed setting
     - GPU capabilities
     - Lookahead depth

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
  - Motion-based Natural Eye shuffle

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
- Motion analysis requires significant processing power
- Processing speed depends on:
  - Video resolution
  - Clip duration
  - Available RAM
  - GPU capabilities (for CUDA versions)
  - Analysis mode and settings

## Troubleshooting

### Common Issues

1. **Web Interface Issues**
   - Check if Python and dependencies are installed
   - Verify port 7860 is not in use
   - Check terminal for error messages

2. **Color/Motion Analysis Issues**
   - Ensure enough disk space for processing
   - Check video file integrity
   - Verify clip format compatibility
   - Monitor GPU memory usage

3. **CUDA Processing Issues**
   - Verify NVIDIA GPU presence
   - Update GPU drivers
   - Use standard versions if CUDA unavailable

4. **Motion Analysis Issues**
   - Verify FFGLITCH is properly installed
   - Check if "ffgac" command works in terminal
   - Ensure FFGLITCH is in system PATH
   - Try running from a new command prompt after PATH updates

### General Solutions
1. If virtual environment fails:
   - Delete 'venv' folder
   - Run install-SVS-cuda.bat again

2. If color/motion analysis is slow:
   - Reduce number of sample frames
   - Use smaller clip sizes
   - Check available memory
   - Try faster analysis settings

3. If joins are incomplete:
   - Check available disk space
   - Verify all clips are valid MP4 files
   - Monitor system resources

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