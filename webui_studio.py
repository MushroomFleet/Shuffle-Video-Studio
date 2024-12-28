import os
import torch
import shutil
from datetime import datetime
from pathlib import Path
import importlib.util
from webui_utils import import_hyphenated_file

class VideoShuffleStudio:
    def __init__(self):
        """Initialize the Video Shuffle Studio core functionality"""
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.temp_dir = os.path.join(self.base_dir, "temp_processing")
        self.output_dir = os.path.join(self.base_dir, "output")
        
        # Create required directories
        os.makedirs(self.temp_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Load core processing modules
        try:
            print("Loading processing modules...")
            self.video_splitter = import_hyphenated_file("video-splitter-cuda.py")
            print("- Loaded video splitter")
            self.beat_splitter = import_hyphenated_file("beat-splitter-cudaV2.py")
            print("- Loaded beat splitter")
            self.shuffle_splits = import_hyphenated_file("shuffle-splits-v2.py")
            print("- Loaded shuffle splits")
            self.shuffle_joiner = import_hyphenated_file("ShuffleJoiner.py")
            print("- Loaded shuffle joiner")
            self.beat_joiner = import_hyphenated_file("beat-shuffle-joiner.py")
            print("- Loaded beat joiner")
            self.color_shuffle = import_hyphenated_file("color_shuffle.py")
            print("- Loaded color shuffle")
        except Exception as e:
            print(f"Error loading modules: {str(e)}")
            raise

    def check_cuda(self):
        """Check for CUDA availability and return status message"""
        if torch.cuda.is_available():
            return f"GPU Available: {torch.cuda.get_device_name(0)}"
        return "CUDA not available. Using CPU processing."

    def create_permanent_file(self, temp_file, prefix):
        """Create a permanent copy of a temporary file with timestamp"""
        if temp_file is None:
            return None
        
        _, ext = os.path.splitext(temp_file.name)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_filename = f"{prefix}_{timestamp}{ext}"
        permanent_path = os.path.join(self.temp_dir, new_filename)
        shutil.copy2(temp_file.name, permanent_path)
        return permanent_path

    def create_output_folder(self, base_name):
        """Create and return a timestamped output folder"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_folder = os.path.join(self.output_dir, f"{base_name}_{timestamp}")
        os.makedirs(output_folder, exist_ok=True)
        return output_folder

    def clean_temp_files(self, *files):
        """Clean up temporary files"""
        for file in files:
            if file and os.path.exists(file):
                try:
                    if os.path.isfile(file):
                        os.remove(file)
                    elif os.path.isdir(file):
                        shutil.rmtree(file)
                except Exception as e:
                    print(f"Warning: Could not clean up {file}: {str(e)}")

    def resolve_folder_path(self, folder_path):
        """Resolve relative folder paths to absolute paths"""
        if not folder_path:
            return None
            
        if not os.path.isabs(folder_path):
            folder_path = os.path.join(self.base_dir, folder_path)
            
        return folder_path if os.path.exists(folder_path) else None

    def get_progress_updater(self):
        """Create a progress update function with timestamps"""
        progress_updates = []
        
        def update_progress(message):
            timestamp = datetime.now().strftime("%H:%M:%S")
            progress_updates.append(f"[{timestamp}] {message}")
            return "\n".join(progress_updates)
            
        return update_progress

    def validate_input_folder(self, folder_path, pattern="*.mp4"):
        """Validate input folder and count matching files"""
        folder = self.resolve_folder_path(folder_path)
        if not folder:
            return False, "Invalid folder path"
            
        files = list(Path(folder).glob(pattern))
        if not files:
            return False, f"No files matching {pattern} found in folder"
            
        return True, f"Found {len(files)} matching files"

    def process_error(self, error, context="operation"):
        """Format error message with context"""
        return f"Error during {context}: {str(error)}"
