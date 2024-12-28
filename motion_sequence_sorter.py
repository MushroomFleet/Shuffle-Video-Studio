import os
from typing import List, Dict, Set, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
import heapq
import random
from motion_manifest_manager import MotionManifest, TransitionScore, ClipMotionData
from motion_vector_extractor import MotionDirection

@dataclass
class SortingConfig:
    """Configuration for motion-based sorting"""
    min_transition_score: float = 0.5
    max_consecutive_static: int = 2
    prefer_intensity_match: bool = True
    allow_reverse_transitions: bool = False
    randomize_equal_scores: bool = True
    transition_lookahead: int = 3

class MotionSequenceSorter:
    def __init__(self, manifest: MotionManifest, config: SortingConfig = None):
        self.manifest = manifest
        self.config = config or SortingConfig()
        self.used_clips: Set[str] = set()
        self.sequence: List[str] = []
        self._transition_cache: Dict[Tuple[str, str], float] = {}
        
    def _get_transition_score(self, from_clip: str, to_clip: str) -> float:
        """Get cached transition score or calculate new one"""
        cache_key = (from_clip, to_clip)
        if cache_key not in self._transition_cache:
            from_data = self.manifest.get_clip_data(from_clip)
            to_data = self.manifest.get_clip_data(to_clip)
            score = self.manifest.calculate_transition_score(from_data, to_data)
            self._transition_cache[cache_key] = score.score
        return self._transition_cache[cache_key]

    def _find_best_next_clip(self, current_clip: str, depth: int = 0) -> Optional[str]:
        """Find the best next clip using lookahead for better global transitions"""
        if depth >= self.config.transition_lookahead:
            return None

        available_clips = [
            clip.clip_path for clip in self.manifest.clips 
            if clip.clip_path not in self.used_clips
        ]
        
        if not available_clips:
            return None

        # Score each potential next clip
        candidates = []
        for next_clip in available_clips:
            # Calculate immediate transition score
            score = self._get_transition_score(current_clip, next_clip)
            
            # Look ahead to future transitions if score is good enough
            if score >= self.config.min_transition_score:
                future_score = 0
                if depth < self.config.transition_lookahead - 1:
                    # Temporarily mark this clip as used
                    self.used_clips.add(next_clip)
                    future_clip = self._find_best_next_clip(next_clip, depth + 1)
                    if future_clip:
                        future_score = self._get_transition_score(next_clip, future_clip)
                    self.used_clips.remove(next_clip)
                
                # Combine immediate and future scores
                combined_score = score
                if future_score > 0:
                    combined_score = (score * 0.7) + (future_score * 0.3)
                
                candidates.append((combined_score, next_clip))

        if not candidates:
            return None

        # Sort candidates by score
        candidates.sort(reverse=True)
        
        # If randomizing equal scores, group them and choose randomly
        if self.config.randomize_equal_scores:
            max_score = candidates[0][0]
            equal_scores = [
                clip for score, clip in candidates 
                if abs(score - max_score) < 0.01
            ]
            if equal_scores:
                return random.choice(equal_scores)

        return candidates[0][1]

    def _calculate_sequence_score(self, sequence: List[str]) -> float:
        """Calculate overall quality score for a sequence"""
        if len(sequence) < 2:
            return 0.0

        total_score = 0.0
        transitions = len(sequence) - 1
        
        for i in range(transitions):
            score = self._get_transition_score(sequence[i], sequence[i + 1])
            total_score += score

        return total_score / transitions

    def _optimize_sequence(self, sequence: List[str], iterations: int = 100) -> List[str]:
        """Try to improve sequence by making local optimizations"""
        best_score = self._calculate_sequence_score(sequence)
        best_sequence = sequence.copy()
        
        for _ in range(iterations):
            # Try swapping random pairs
            if len(sequence) < 2:
                break
                
            # Choose random segment to optimize
            start = random.randint(0, len(sequence) - 2)
            length = min(random.randint(2, 4), len(sequence) - start)
            
            # Get segments
            before = sequence[:start]
            segment = sequence[start:start + length]
            after = sequence[start + length:]
            
            # Try different permutations of the segment
            for i in range(length - 1):
                for j in range(i + 1, length):
                    # Swap clips
                    new_segment = segment.copy()
                    new_segment[i], new_segment[j] = new_segment[j], new_segment[i]
                    
                    # Create and score new sequence
                    new_sequence = before + new_segment + after
                    new_score = self._calculate_sequence_score(new_sequence)
                    
                    if new_score > best_score:
                        best_score = new_score
                        best_sequence = new_sequence.copy()

        return best_sequence

    def sort_clips_natural_eye(self) -> List[str]:
        """
        Sort clips using the Natural Eye algorithm to create smooth visual flow.
        Returns list of clip paths in optimal order.
        """
        self.used_clips.clear()
        self.sequence.clear()
        self._transition_cache.clear()
        
        # Find best starting clip (one with strong directional motion)
        start_candidates = []
        for clip in self.manifest.clips:
            start_motion = clip.start_motion
            if start_motion.primary_direction != MotionDirection.STATIC:
                score = start_motion.intensity * start_motion.confidence
                start_candidates.append((score, clip.clip_path))
        
        if not start_candidates:
            # Fallback to random start if no good candidates
            self.sequence.append(random.choice(self.manifest.clips).clip_path)
        else:
            # Choose from top candidates
            start_candidates.sort(reverse=True)
            top_candidates = [
                clip for score, clip in start_candidates[:3]
            ]
            self.sequence.append(random.choice(top_candidates))
        
        self.used_clips.add(self.sequence[0])
        
        # Build sequence using lookahead for better global transitions
        static_count = 0
        while len(self.used_clips) < len(self.manifest.clips):
            current_clip = self.sequence[-1]
            next_clip = self._find_best_next_clip(current_clip)
            
            if not next_clip:
                # If no good transition found, try a random unused clip
                unused_clips = [
                    clip.clip_path for clip in self.manifest.clips 
                    if clip.clip_path not in self.used_clips
                ]
                if not unused_clips:
                    break
                next_clip = random.choice(unused_clips)
                static_count += 1
            else:
                static_count = 0
            
            if static_count > self.config.max_consecutive_static:
                # Force a directional transition to avoid static sequences
                direction_clips = [
                    clip.clip_path for clip in self.manifest.clips
                    if clip.clip_path not in self.used_clips and
                    clip.start_motion.primary_direction != MotionDirection.STATIC
                ]
                if direction_clips:
                    next_clip = random.choice(direction_clips)
                    static_count = 0
            
            self.sequence.append(next_clip)
            self.used_clips.add(next_clip)
        
        # Optimize the sequence
        self.sequence = self._optimize_sequence(self.sequence)
        
        return self.sequence

    def get_transition_report(self) -> List[Dict]:
        """Generate detailed report of transitions in the sequence"""
        if len(self.sequence) < 2:
            return []

        report = []
        for i in range(len(self.sequence) - 1):
            from_clip = self.manifest.get_clip_data(self.sequence[i])
            to_clip = self.manifest.get_clip_data(self.sequence[i + 1])
            score = self.manifest.calculate_transition_score(from_clip, to_clip)
            
            report.append({
                "from_clip": self.sequence[i],
                "to_clip": self.sequence[i + 1],
                "score": score.score,
                "direction_match": score.direction_match,
                "intensity_match": score.intensity_match,
                "notes": score.notes
            })

        return report

    def apply_sequence_to_files(self, output_dir: Path) -> None:
        """Apply the sorted sequence to actual files"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for i, clip_path in enumerate(self.sequence):
            source = Path(clip_path)
            if not source.exists():
                print(f"Warning: Source file not found: {clip_path}")
                continue
                
            # Create new filename with sequence number
            dest = output_dir / f"sequence_{i:04d}{source.suffix}"
            
            try:
                # Create hard link to save space, fall back to copy if needed
                try:
                    os.link(source, dest)
                except OSError:
                    import shutil
                    shutil.copy2(source, dest)
            except Exception as e:
                print(f"Error processing {clip_path}: {str(e)}")

# Example usage
if __name__ == "__main__":
    # Load manifest
    manifest = MotionManifest(Path("motion_manifest.json"))
    
    # Configure sorting
    config = SortingConfig(
        min_transition_score=0.5,
        max_consecutive_static=2,
        prefer_intensity_match=True,
        randomize_equal_scores=True,
        transition_lookahead=3
    )
    
    # Create sorter and sort clips
    sorter = MotionSequenceSorter(manifest, config)
    sequence = sorter.sort_clips_natural_eye()
    
    # Generate and print transition report
    report = sorter.get_transition_report()
    print("\nTransition Report:")
    for transition in report:
        print(f"\nFrom: {Path(transition['from_clip']).name}")
        print(f"To: {Path(transition['to_clip']).name}")
        print(f"Score: {transition['score']:.2f}")
        print(f"Notes: {transition['notes']}")
    
    # Apply sequence to files
    output_dir = Path("sorted_output")
    sorter.apply_sequence_to_files(output_dir)
