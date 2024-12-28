import subprocess
import os
import json
import numpy as np
from typing import Dict, List, Tuple
from enum import Enum
import tempfile
from pathlib import Path

class MotionDirection(Enum):
    NORTH = "N"
    NORTHEAST = "NE"
    EAST = "E"
    SOUTHEAST = "SE"
    SOUTH = "S"
    SOUTHWEST = "SW"
    WEST = "W"
    NORTHWEST = "NW"
    STATIC = "static"
    COMPLEX = "complex"

    @staticmethod
    def from_angle(angle: float) -> 'MotionDirection':
        """Convert an angle in radians to a cardinal direction.
        Angle 0 points East, going counterclockwise."""
        # Convert angle to degrees and normalize to 0-360
        degrees = (np.degrees(angle) + 360) % 360
        
        # Define direction sectors (each 45 degrees)
        if 337.5 <= degrees or degrees < 22.5:
            return MotionDirection.EAST
        elif 22.5 <= degrees < 67.5:
            return MotionDirection.NORTHEAST
        elif 67.5 <= degrees < 112.5:
            return MotionDirection.NORTH
        elif 112.5 <= degrees < 157.5:
            return MotionDirection.NORTHWEST
        elif 157.5 <= degrees < 202.5:
            return MotionDirection.WEST
        elif 202.5 <= degrees < 247.5:
            return MotionDirection.SOUTHWEST
        elif 247.5 <= degrees < 292.5:
            return MotionDirection.SOUTH
        else:  # 292.5 <= degrees < 337.5
            return MotionDirection.SOUTHEAST
            
    def get_opposite(self) -> 'MotionDirection':
        """Get the opposite cardinal direction."""
        opposites = {
            MotionDirection.NORTH: MotionDirection.SOUTH,
            MotionDirection.NORTHEAST: MotionDirection.SOUTHWEST,
            MotionDirection.EAST: MotionDirection.WEST,
            MotionDirection.SOUTHEAST: MotionDirection.NORTHWEST,
            MotionDirection.SOUTH: MotionDirection.NORTH,
            MotionDirection.SOUTHWEST: MotionDirection.NORTHEAST,
            MotionDirection.WEST: MotionDirection.EAST,
            MotionDirection.NORTHWEST: MotionDirection.SOUTHEAST,
            MotionDirection.STATIC: MotionDirection.STATIC,
            MotionDirection.COMPLEX: MotionDirection.COMPLEX
        }
        return opposites[self]

class MotionSummary:
    def __init__(self, 
                 primary_direction: MotionDirection,
                 secondary_direction: MotionDirection = None,
                 intensity: float = 0.0,
                 confidence: float = 0.0):
        self.primary_direction = primary_direction
        self.secondary_direction = secondary_direction
        self.intensity = intensity
        self.confidence = confidence

    def to_dict(self) -> Dict:
        return {
            "primary_direction": self.primary_direction.value,
            "secondary_direction": self.secondary_direction.value if self.secondary_direction else None,
            "intensity": float(self.intensity),
            "confidence": float(self.confidence)
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'MotionSummary':
        return cls(
            primary_direction=MotionDirection(data["primary_direction"]),
            secondary_direction=MotionDirection(data["secondary_direction"]) if data["secondary_direction"] else None,
            intensity=data["intensity"],
            confidence=data["confidence"]
        )

class ClipMotionData:
    def __init__(self, 
                 clip_path: str,
                 start_motion: MotionSummary = None,
                 end_motion: MotionSummary = None,
                 frame_count: int = 0):
        self.clip_path = clip_path
        self.start_motion = start_motion
        self.end_motion = end_motion
        self.frame_count = frame_count

    def to_dict(self) -> Dict:
        return {
            "clip_path": self.clip_path,
            "start_motion": self.start_motion.to_dict() if self.start_motion else None,
            "end_motion": self.end_motion.to_dict() if self.end_motion else None,
            "frame_count": self.frame_count
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'ClipMotionData':
        return cls(
            clip_path=data["clip_path"],
            start_motion=MotionSummary.from_dict(data["start_motion"]) if data["start_motion"] else None,
            end_motion=MotionSummary.from_dict(data["end_motion"]) if data["end_motion"] else None,
            frame_count=data["frame_count"]
        )

class MotionVectorExtractor:
    def __init__(self, speed_mode: str = "balanced"):
        """
        Initialize the motion vector extractor.
        
        Args:
            speed_mode (str): One of "fast", "balanced", or "precise"
                - fast: Analyze fewer frames, use simpler analysis
                - balanced: Default analysis with moderate detail
                - precise: Detailed analysis of all frames
        """
        self.speed_mode = speed_mode
        self.temp_dir = Path(tempfile.gettempdir()) / "motion_analysis"
        self.temp_dir.mkdir(exist_ok=True)
        
        # Configure analysis parameters based on speed mode
        self.config = {
            "fast": {
                "sample_rate": 5,  # Analyze every 5th frame
                "vector_threshold": 0.5,  # Higher threshold for motion detection
                "confidence_threshold": 0.6
            },
            "balanced": {
                "sample_rate": 2,
                "vector_threshold": 0.3,
                "confidence_threshold": 0.7
            },
            "precise": {
                "sample_rate": 1,  # Analyze every frame
                "vector_threshold": 0.2,
                "confidence_threshold": 0.8
            }
        }[speed_mode]

    def extract_motion_vectors(self, video_path: str) -> List[Dict]:
        """
        Extract motion vectors from a video file using FFGAC.
        
        Args:
            video_path (str): Path to the input video file
            
        Returns:
            List[Dict]: List of motion vectors per frame
        """
        temp_mpg = self.temp_dir / "temp.mpg"
        temp_json = self.temp_dir / "temp.json"
        
        try:
            # Convert to MPG with specific settings for motion vector extraction
            subprocess.run([
                'ffgac', '-i', video_path,
                '-an', '-mpv_flags', '+nopimb+forcemv',
                '-qscale:v', '0',
                '-g', '1000',
                '-vcodec', 'mpeg2video',
                '-f', 'rawvideo',
                '-y', str(temp_mpg)
            ], check=True)
            
            # Extract motion vectors
            subprocess.run([
                'ffedit', '-i', str(temp_mpg),
                '-f', 'mv:0',
                '-e', str(temp_json)
            ], check=True)
            
            # Load and parse the motion vector data
            with open(temp_json, 'r') as f:
                data = json.load(f)
            
            vectors = []
            frames = data['streams'][0]['frames']
            
            # Convert numpy types to Python native types
            def convert_to_native(obj):
                if isinstance(obj, (np.int_, np.intc, np.intp, np.int8,
                    np.int16, np.int32, np.int64, np.uint8,
                    np.uint16, np.uint32, np.uint64)):
                    return int(obj)
                elif isinstance(obj, (np.float_, np.float16, np.float32,
                    np.float64)):
                    return float(obj)
                elif isinstance(obj, (np.bool_)):
                    return bool(obj)
                elif isinstance(obj, (np.ndarray,)):
                    return convert_to_native(obj.tolist())
                elif isinstance(obj, (list, tuple)):
                    return [convert_to_native(item) for item in obj]
                elif isinstance(obj, dict):
                    return {key: convert_to_native(value) for key, value in obj.items()}
                return obj
            
            for idx, frame in enumerate(frames):
                if idx % self.config["sample_rate"] == 0:  # Sample based on speed mode
                    if 'mv' in frame and 'forward' in frame['mv']:
                        vectors.append(frame['mv']['forward'])
                    else:
                        vectors.append([])
            
            return vectors
            
        finally:
            # Cleanup temporary files
            for temp_file in [temp_mpg, temp_json]:
                if temp_file.exists():
                    temp_file.unlink()

    def analyze_motion_segment(self, 
                             vectors: List[List], 
                             start_frame: int, 
                             end_frame: int) -> MotionSummary:
        """
        Analyze motion vectors for a segment of frames to determine dominant direction.
        
        Args:
            vectors: List of motion vectors
            start_frame: Starting frame index
            end_frame: Ending frame index
            
        Returns:
            MotionSummary object containing direction and intensity information
        """
        if not vectors or end_frame <= start_frame:
            return MotionSummary(MotionDirection.STATIC, intensity=0.0, confidence=1.0)
        
        # Aggregate motion vectors for the segment
        x_motions = []
        y_motions = []
        
        for frame_vectors in vectors[start_frame:end_frame]:
            if not frame_vectors:
                continue
                
            frame_x = []
            frame_y = []
            
            for row in frame_vectors:
                for mv in row:
                    if isinstance(mv, list) and len(mv) >= 2:
                        if abs(mv[0]) > self.config["vector_threshold"] or \
                           abs(mv[1]) > self.config["vector_threshold"]:
                            frame_x.append(mv[0])
                            frame_y.append(mv[1])
            
            if frame_x:
                x_motions.extend(frame_x)
                y_motions.extend(frame_y)
        
        if not x_motions:
            return MotionSummary(MotionDirection.STATIC, intensity=0.0, confidence=1.0)
        
        # Calculate average motion
        avg_x = np.mean(x_motions)
        avg_y = np.mean(y_motions)
        
        # Calculate motion intensity
        intensity = np.sqrt(avg_x**2 + avg_y**2)
        
        # Determine primary and secondary directions
        angle = np.arctan2(avg_y, avg_x)
        confidence = min(1.0, intensity / 2.0)  # Scale confidence based on intensity
        
        # Convert angle to cardinal direction
        if intensity < self.config["vector_threshold"]:
            primary = MotionDirection.STATIC
            secondary = None
        else:
            # Calculate primary direction from angle
            primary = MotionDirection.from_angle(angle)
            
            # Calculate secondary direction
            # Use the nearest adjacent cardinal direction based on relative magnitudes
            if primary in [MotionDirection.NORTH, MotionDirection.SOUTH]:
                secondary = MotionDirection.EAST if avg_x > 0 else MotionDirection.WEST
            elif primary in [MotionDirection.EAST, MotionDirection.WEST]:
                secondary = MotionDirection.NORTH if avg_y < 0 else MotionDirection.SOUTH
            else:
                # For diagonal primaries, secondary is the stronger of the cardinal directions
                if abs(avg_x) > abs(avg_y):
                    secondary = MotionDirection.EAST if avg_x > 0 else MotionDirection.WEST
                else:
                    secondary = MotionDirection.NORTH if avg_y < 0 else MotionDirection.SOUTH
        
        if intensity < self.config["vector_threshold"]:
            primary = MotionDirection.STATIC
            secondary = None
        
        return MotionSummary(
            primary_direction=primary,
            secondary_direction=secondary,
            intensity=intensity,
            confidence=confidence
        )

    def analyze_clip(self, video_path: str, analysis_window: int = 30) -> ClipMotionData:
        """
        Analyze motion vectors for an entire clip, focusing on start and end segments.
        
        Args:
            video_path: Path to the video file
            analysis_window: Number of frames to analyze at start and end
            
        Returns:
            ClipMotionData object containing motion analysis
        """
        vectors = self.extract_motion_vectors(video_path)
        
        if not vectors:
            return ClipMotionData(
                clip_path=video_path,
                start_motion=MotionSummary(MotionDirection.STATIC),
                end_motion=MotionSummary(MotionDirection.STATIC),
                frame_count=0
            )
        
        # Analyze start segment
        start_motion = self.analyze_motion_segment(
            vectors, 
            0, 
            min(analysis_window, len(vectors))
        )
        
        # Analyze end segment
        end_motion = self.analyze_motion_segment(
            vectors,
            max(0, len(vectors) - analysis_window),
            len(vectors)
        )
        
        return ClipMotionData(
            clip_path=video_path,
            start_motion=start_motion,
            end_motion=end_motion,
            frame_count=len(vectors)
        )

    def batch_analyze_clips(self, 
                          clip_paths: List[str], 
                          manifest_path: str = None) -> List[ClipMotionData]:
        """
        Analyze multiple clips and optionally save to a manifest file.
        
        Args:
            clip_paths: List of paths to video clips
            manifest_path: Optional path to save motion data manifest
            
        Returns:
            List of ClipMotionData objects
        """
        results = []
        
        for clip_path in clip_paths:
            try:
                motion_data = self.analyze_clip(clip_path)
                results.append(motion_data)
            except Exception as e:
                print(f"Error analyzing {clip_path}: {str(e)}")
                continue
        
        if manifest_path:
            self.save_manifest(results, manifest_path)
        
        return results

    def save_manifest(self, motion_data: List[ClipMotionData], manifest_path: str):
        """Save motion analysis data to a JSON manifest file."""
        manifest = {
            "speed_mode": self.speed_mode,
            "clips": [data.to_dict() for data in motion_data]
        }
        
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)

    def load_manifest(self, manifest_path: str) -> List[ClipMotionData]:
        """Load motion analysis data from a JSON manifest file."""
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
            
        return [ClipMotionData.from_dict(data) for data in manifest["clips"]]

# Example usage
if __name__ == "__main__":
    extractor = MotionVectorExtractor(speed_mode="balanced")
    
    # Example with a single clip
    clip_path = "example.mp4"
    if os.path.exists(clip_path):
        motion_data = extractor.analyze_clip(clip_path)
        print(f"Clip: {clip_path}")
        print(f"Start motion: {motion_data.start_motion.primary_direction}")
        print(f"End motion: {motion_data.end_motion.primary_direction}")
        print(f"Motion intensity: {motion_data.end_motion.intensity:.2f}")