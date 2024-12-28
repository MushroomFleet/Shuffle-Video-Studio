import os
import importlib.util
from pathlib import Path
from typing import Optional, Tuple, List, Any
import shutil
from datetime import datetime

class InputSimulator:
    """Simulates user input for CLI operations"""
    def __init__(self, inputs):
        self.inputs = inputs
        self.input_index = 0
        self.buffer = ""
    
    def __call__(self, prompt=""):
        if self.input_index < len(self.inputs):
            result = str(self.inputs[self.input_index]) + "\n"
            self.input_index += 1
            return result
        return "\n"
    
    def readline(self):
        if self.input_index < len(self.inputs):
            result = str(self.inputs[self.input_index]) + "\n"
            self.input_index += 1
            return result
        return "\n"

    def read(self, size=-1):
        if self.input_index < len(self.inputs):
            result = str(self.inputs[self.input_index]) + "\n"
            self.input_index += 1
            return result
        return "\n"

def import_hyphenated_file(filename: str) -> Any:
    """Import python files that contain hyphens in their names"""
    try:
        module_name = filename.replace('.py', '').replace('-', '_')
        spec = importlib.util.spec_from_file_location(module_name, filename)
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load spec for module {filename}")
        
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
        
    except Exception as e:
        raise ImportError(f"Error importing {filename}: {str(e)}")

def validate_video_file(file_path: Path) -> Tuple[bool, str]:
    """Validate a video file exists and has correct extension"""
    if not file_path.exists():
        return False, f"File not found: {file_path}"
    
    if not file_path.suffix.lower() == '.mp4':
        return False, f"Invalid file type: {file_path.suffix} (expected .mp4)"
    
    try:
        size = file_path.stat().st_size
        if size == 0:
            return False, f"File is empty: {file_path}"
    except Exception as e:
        return False, f"Error checking file: {str(e)}"
    
    return True, "File valid"

def validate_audio_file(file_path: Path) -> Tuple[bool, str]:
    """Validate an audio file exists and has correct extension"""
    if not file_path.exists():
        return False, f"File not found: {file_path}"
    
    if not file_path.suffix.lower() in ['.mp3', '.wav']:
        return False, f"Invalid file type: {file_path.suffix} (expected .mp3 or .wav)"
    
    try:
        size = file_path.stat().st_size
        if size == 0:
            return False, f"File is empty: {file_path}"
    except Exception as e:
        return False, f"Error checking file: {str(e)}"
    
    return True, "File valid"

def create_timestamped_path(base_path: Path, prefix: str = "", suffix: str = "") -> Path:
    """Create a path with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{timestamp}{suffix}" if prefix else f"{timestamp}{suffix}"
    return base_path / filename

def ensure_directory(path: Path) -> Tuple[bool, str]:
    """Ensure a directory exists and is writable"""
    try:
        path.mkdir(parents=True, exist_ok=True)
        # Test write permissions
        test_file = path / ".write_test"
        test_file.touch()
        test_file.unlink()
        return True, f"Directory ready: {path}"
    except Exception as e:
        return False, f"Directory error: {str(e)}"

def clean_directory(path: Path, pattern: str = "*") -> Tuple[int, List[str]]:
    """Clean up files in a directory matching a pattern"""
    failed = []
    count = 0
    
    try:
        for item in path.glob(pattern):
            try:
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
                count += 1
            except Exception as e:
                failed.append(f"{item}: {str(e)}")
    except Exception as e:
        failed.append(f"Error accessing directory: {str(e)}")
    
    return count, failed

def format_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"

def get_file_info(file_path: Path) -> dict:
    """Get detailed file information"""
    try:
        stats = file_path.stat()
        return {
            "name": file_path.name,
            "size": format_size(stats.st_size),
            "created": datetime.fromtimestamp(stats.st_ctime).strftime("%Y-%m-%d %H:%M:%S"),
            "modified": datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        return {
            "name": file_path.name,
            "error": str(e)
        }

class ProgressTracker:
    """Track and format progress updates"""
    def __init__(self):
        self.start_time = datetime.now()
        self.updates = []
        
    def update(self, message: str, level: str = "info") -> str:
        """Add a progress update with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = "✓" if level == "success" else "⚠" if level == "warning" else "✗" if level == "error" else "→"
        update = f"[{timestamp}] {prefix} {message}"
        self.updates.append(update)
        return "\n".join(self.updates)
    
    def get_elapsed(self) -> str:
        """Get elapsed time formatted"""
        elapsed = datetime.now() - self.start_time
        return str(elapsed).split('.')[0]  # Remove microseconds

def create_file_manifest(directory: Path, pattern: str = "*.mp4") -> dict:
    """Create a manifest of files in a directory"""
    manifest = {
        "directory": str(directory),
        "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "pattern": pattern,
        "files": []
    }
    
    try:
        files = list(directory.glob(pattern))
        total_size = 0
        
        for file_path in files:
            info = get_file_info(file_path)
            manifest["files"].append(info)
            
            # Add size in bytes for total
            try:
                total_size += file_path.stat().st_size
            except:
                pass
        
        manifest["total_files"] = len(files)
        manifest["total_size"] = format_size(total_size)
        manifest["status"] = "success"
        
    except Exception as e:
        manifest["status"] = "error"
        manifest["error"] = str(e)
    
    return manifest

# Example usage
if __name__ == "__main__":
    # Test file validation
    video_path = Path("test.mp4")
    print(validate_video_file(video_path))
    
    # Test directory functions
    temp_dir = Path("temp")
    success, message = ensure_directory(temp_dir)
    print(message)
    
    if success:
        # Test progress tracking
        progress = ProgressTracker()
        progress.update("Starting process...")
        progress.update("Warning example", "warning")
        progress.update("Error example", "error")
        progress.update("Success example", "success")
        print("\nProgress Test:")
        print(progress.updates)
        
        # Clean up
        count, failed = clean_directory(temp_dir)
        print(f"\nCleaned {count} items")
        if failed:
            print("Failed items:", failed)
