import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
import numpy as np
from motion_vector_extractor import MotionDirection, MotionSummary, ClipMotionData

@dataclass
class TransitionScore:
    """Stores transition compatibility score between two clips"""
    from_clip: str
    to_clip: str
    score: float
    direction_match: bool
    intensity_match: bool
    notes: str = ""

    def to_dict(self) -> Dict:
        return {
            "from_clip": str(self.from_clip),
            "to_clip": str(self.to_clip),
            "score": float(self.score),
            "direction_match": bool(self.direction_match),
            "intensity_match": bool(self.intensity_match),
            "notes": str(self.notes)
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'TransitionScore':
        return cls(**data)

class MotionManifest:
    def __init__(self, manifest_path: Path = None):
        self.manifest_path = manifest_path
        self.clips: List[ClipMotionData] = []
        self.transitions: List[TransitionScore] = []
        self.metadata: Dict = {
            "created": datetime.now().isoformat(),
            "last_modified": datetime.now().isoformat(),
            "clip_count": 0,
            "version": "1.0",
            "analysis_settings": {}
        }
        
        if manifest_path and manifest_path.exists():
            self.load()

    def add_clip(self, clip_data: ClipMotionData) -> None:
        """Add or update a clip's motion data in the manifest"""
        # Check if clip already exists
        existing_idx = next(
            (i for i, c in enumerate(self.clips) 
             if c.clip_path == clip_data.clip_path), 
            None
        )
        
        if existing_idx is not None:
            self.clips[existing_idx] = clip_data
        else:
            self.clips.append(clip_data)
            
        self.metadata["clip_count"] = len(self.clips)
        self.metadata["last_modified"] = datetime.now().isoformat()

    def add_transition_score(self, transition: TransitionScore) -> None:
        """Add or update a transition score between clips"""
        # Remove any existing transition between these clips
        self.transitions = [
            t for t in self.transitions 
            if not (t.from_clip == transition.from_clip and 
                   t.to_clip == transition.to_clip)
        ]
        self.transitions.append(transition)

    def get_clip_data(self, clip_path: str) -> Optional[ClipMotionData]:
        """Retrieve motion data for a specific clip"""
        return next(
            (clip for clip in self.clips if clip.clip_path == clip_path), 
            None
        )

    def get_compatible_transitions(self, 
                                 clip_path: str, 
                                 min_score: float = 0.5
                                ) -> List[TransitionScore]:
        """Get all compatible transitions from a given clip"""
        return [
            t for t in self.transitions 
            if t.from_clip == clip_path and t.score >= min_score
        ]

    def calculate_transition_score(self,
                                 from_clip: ClipMotionData,
                                 to_clip: ClipMotionData
                                ) -> TransitionScore:
        """Calculate transition compatibility score between two clips"""
        if not (from_clip and to_clip):
            return TransitionScore(
                from_clip=from_clip.clip_path if from_clip else "",
                to_clip=to_clip.clip_path if to_clip else "",
                score=0.0,
                direction_match=False,
                intensity_match=False,
                notes="Invalid clip data"
            )

        # Get end motion of first clip and start motion of second clip
        end_motion = from_clip.end_motion
        start_motion = to_clip.start_motion

        # Initialize scoring components
        direction_score = 0.0
        intensity_score = 0.0
        direction_match = False
        intensity_match = False
        notes = []

        # Check for opposing directions (ideal for eye tracking)
        if end_motion.primary_direction != MotionDirection.STATIC:
            if start_motion.primary_direction == end_motion.primary_direction.get_opposite():
                direction_score = 1.0
                direction_match = True
                notes.append("Perfect direction match")
            else:
                # Calculate angular difference for partial matching
                angle_diff = self._calculate_direction_angle_diff(
                    end_motion.primary_direction,
                    start_motion.primary_direction
                )
                direction_score = 1.0 - (angle_diff / 180.0)
                notes.append(f"Partial direction match ({angle_diff:.1f}°)")

        # Compare motion intensities
        intensity_diff = abs(end_motion.intensity - start_motion.intensity)
        intensity_score = 1.0 - min(1.0, intensity_diff / 2.0)
        intensity_match = intensity_diff < 0.5
        
        if intensity_match:
            notes.append("Intensity matched")
        else:
            notes.append(f"Intensity difference: {intensity_diff:.2f}")

        # Combine scores with weights
        final_score = (direction_score * 0.7) + (intensity_score * 0.3)

        return TransitionScore(
            from_clip=from_clip.clip_path,
            to_clip=to_clip.clip_path,
            score=final_score,
            direction_match=direction_match,
            intensity_match=intensity_match,
            notes="; ".join(notes)
        )

    def _calculate_direction_angle_diff(self,
                                      dir1: MotionDirection,
                                      dir2: MotionDirection
                                     ) -> float:
        """Calculate the angular difference between two directions"""
        if dir1 == MotionDirection.STATIC or dir2 == MotionDirection.STATIC:
            return 180.0  # Maximum difference
            
        # Define angles for each direction (in degrees, clockwise from North)
        direction_angles = {
            MotionDirection.NORTH: 0,
            MotionDirection.NORTHEAST: 45,
            MotionDirection.EAST: 90,
            MotionDirection.SOUTHEAST: 135,
            MotionDirection.SOUTH: 180,
            MotionDirection.SOUTHWEST: 225,
            MotionDirection.WEST: 270,
            MotionDirection.NORTHWEST: 315,
        }
        
        if dir1 not in direction_angles or dir2 not in direction_angles:
            return 180.0  # Maximum difference for complex/invalid directions
            
        angle1 = direction_angles[dir1]
        angle2 = direction_angles[dir2]
        
        # Calculate smallest angular difference
        diff = abs(angle1 - angle2)
        return min(diff, 360 - diff)

    def analyze_all_transitions(self) -> None:
        """Calculate transition scores between all clips"""
        self.transitions.clear()
        
        for i, from_clip in enumerate(self.clips):
            for to_clip in self.clips[i+1:]:  # Only analyze forward transitions
                score = self.calculate_transition_score(from_clip, to_clip)
                self.add_transition_score(score)

    def save(self, path: Optional[Path] = None) -> None:
        """Save manifest to JSON file"""
        save_path = path or self.manifest_path
        if not save_path:
            raise ValueError("No manifest path specified")

        manifest_data = {
            "metadata": self.metadata,
            "clips": [clip.to_dict() for clip in self.clips],
            "transitions": [transition.to_dict() for transition in self.transitions]
        }

        with open(save_path, 'w') as f:
            json.dump(manifest_data, f, indent=2)

    def load(self, path: Optional[Path] = None) -> None:
        """Load manifest from JSON file"""
        load_path = path or self.manifest_path
        if not load_path or not load_path.exists():
            raise ValueError("Invalid manifest path")

        with open(load_path, 'r') as f:
            data = json.load(f)

        self.metadata = data.get("metadata", {})
        self.clips = [ClipMotionData.from_dict(c) for c in data.get("clips", [])]
        self.transitions = [TransitionScore.from_dict(t) for t in data.get("transitions", [])]

    def get_statistics(self) -> Dict:
        """Generate statistics about the manifest"""
        return {
            "total_clips": len(self.clips),
            "total_transitions": len(self.transitions),
            "avg_transition_score": np.mean([t.score for t in self.transitions]) if self.transitions else 0,
            "direction_distributions": self._calculate_direction_distributions(),
            "metadata": self.metadata
        }

    def _calculate_direction_distributions(self) -> Dict:
        """Calculate distribution of motion directions across clips"""
        directions = {
            "start": {},
            "end": {}
        }
        
        for clip in self.clips:
            # Count start directions
            start_dir = clip.start_motion.primary_direction.value
            directions["start"][start_dir] = directions["start"].get(start_dir, 0) + 1
            
            # Count end directions
            end_dir = clip.end_motion.primary_direction.value
            directions["end"][end_dir] = directions["end"].get(end_dir, 0) + 1

        return directions

# Example usage
if __name__ == "__main__":
    manifest = MotionManifest(Path("motion_manifest.json"))
    
    # Example: Load some test data
    test_clip = ClipMotionData(
        clip_path="test.mp4",
        start_motion=MotionSummary(
            primary_direction=MotionDirection.EAST,
            intensity=0.8,
            confidence=0.9
        ),
        end_motion=MotionSummary(
            primary_direction=MotionDirection.WEST,
            intensity=0.7,
            confidence=0.85
        ),
        frame_count=100
    )
    
    manifest.add_clip(test_clip)
    manifest.save()
    
    # Print statistics
    stats = manifest.get_statistics()
    print("\nManifest Statistics:")
    print(f"Total Clips: {stats['total_clips']}")
    print(f"Total Transitions: {stats['total_transitions']}")
    print("\nDirection Distributions:")
    print(json.dumps(stats['direction_distributions'], indent=2))