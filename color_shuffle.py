import os
import glob
import shutil
from pathlib import Path
import numpy as np
import cv2
from moviepy.editor import VideoFileClip
from tqdm import tqdm
import colorsys
from sklearn.cluster import KMeans
import multiprocessing

# Disable parallel processing in scikit-learn and joblib
os.environ["LOKY_MAX_CPU_COUNT"] = "1"
os.environ["JOBLIB_TEMP_FOLDER"] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp")
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

# Create temp directory if it doesn't exist
if "JOBLIB_TEMP_FOLDER" in os.environ:
    os.makedirs(os.environ["JOBLIB_TEMP_FOLDER"], exist_ok=True)

def extract_dominant_colors(video_path, num_colors=3, sample_frames=10):
    """Extract dominant colors from video frames using K-means clustering."""
    try:
        # Disable multiprocessing in scikit-learn
        os.environ["LOKY_MAX_CPU_COUNT"] = "1"
        
        video = VideoFileClip(video_path)
        duration = video.duration
        frames = []
        
        # Sample frames evenly throughout the video
        frame_times = np.linspace(0, duration-1, sample_frames)
        for time in frame_times:
            frame = video.get_frame(time)
            # Downsample frame to reduce processing time
            frame = cv2.resize(frame, (160, 90))  # Scale to smaller size
            frames.append(frame)
        
        # Reshape frames for color analysis
        pixels = np.vstack([frame.reshape(-1, 3) for frame in frames])
        
        # Use K-means with minimal iterations
        kmeans = KMeans(
            n_clusters=num_colors,
            n_init=1,           # Reduce number of initializations
            max_iter=100,       # Limit maximum iterations
            algorithm='lloyd'   # Use classic K-means algorithm
        )
        kmeans.fit(pixels)
        
        # Get the RGB values of the cluster centers
        colors = kmeans.cluster_centers_
        
        # Convert to HSV for better color comparison
        hsv_colors = []
        for color in colors:
            hsv = colorsys.rgb_to_hsv(color[0]/255, color[1]/255, color[2]/255)
            hsv_colors.append(hsv)
        
        video.close()
        return hsv_colors
        
    except Exception as e:
        print(f"Error processing {video_path}: {str(e)}")
        return None

def color_distance(hsv1, hsv2):
    """Calculate distance between two HSV colors."""
    # Weight hue more heavily in the distance calculation
    h_weight, s_weight, v_weight = 2.0, 1.0, 1.0
    
    # Handle hue wrap-around
    h_diff = min(abs(hsv1[0] - hsv2[0]), 1 - abs(hsv1[0] - hsv2[0]))
    s_diff = abs(hsv1[1] - hsv2[1])
    v_diff = abs(hsv1[2] - hsv2[2])
    
    return (h_weight * h_diff) + (s_weight * s_diff) + (v_weight * v_diff)

def get_transition_target_colors(transition_type):
    """Get target colors for different transition types."""
    if transition_type == "rainbow":
        return [
            (0.0, 1.0, 1.0),    # Red
            (0.167, 1.0, 1.0),  # Yellow
            (0.333, 1.0, 1.0),  # Green
            (0.5, 1.0, 1.0),    # Cyan
            (0.667, 1.0, 1.0),  # Blue
            (0.833, 1.0, 1.0),  # Magenta
        ]
    elif transition_type == "sunset":
        return [
            (0.05, 0.8, 1.0),   # Orange-red
            (0.08, 0.7, 0.9),   # Deep orange
            (0.11, 0.6, 0.8),   # Warm orange
            (0.15, 0.5, 0.7),   # Soft orange
            (0.2, 0.4, 0.6),    # Pink-orange
            (0.7, 0.3, 0.5),    # Purple-blue
        ]
    elif transition_type == "ocean":
        return [
            (0.5, 0.3, 0.9),    # Light blue
            (0.5, 0.5, 0.8),    # Medium blue
            (0.5, 0.7, 0.7),    # Ocean blue
            (0.55, 0.8, 0.6),   # Deep blue
            (0.6, 0.9, 0.5),    # Dark blue
            (0.65, 1.0, 0.4),   # Navy blue
        ]
    return None

def color_based_shuffle(input_folder, output_folder, mode="similarity", transition_type=None):
    """
    Shuffle video clips based on color analysis.
    
    Args:
        input_folder (str): Path to input folder containing clips
        output_folder (str): Path to output folder for shuffled clips
        mode (str): Either "similarity" or "transition"
        transition_type (str): Type of color transition (for transition mode)
    """
    # Create output directory
    os.makedirs(output_folder, exist_ok=True)
    
    # Get list of clips
    clips = glob.glob(os.path.join(input_folder, 'clip_????.mp4'))
    if not clips:
        print("No clips found in input folder!")
        return
    
    print(f"\nAnalyzing colors in {len(clips)} clips...")
    
    # Extract dominant colors from all clips
    clip_colors = {}
    failed_clips = []
    
    with tqdm(total=len(clips), desc="Processing clips") as pbar:
        for clip in clips:
            try:
                colors = extract_dominant_colors(clip)
                if colors:
                    clip_colors[clip] = colors
                else:
                    failed_clips.append(clip)
            except Exception as e:
                print(f"\nError processing {clip}: {str(e)}")
                failed_clips.append(clip)
            pbar.update(1)
    
    if failed_clips:
        print(f"\nWarning: Failed to process {len(failed_clips)} clips:")
        for clip in failed_clips[:5]:  # Show first 5 failed clips
            print(f"- {os.path.basename(clip)}")
        if len(failed_clips) > 5:
            print(f"... and {len(failed_clips) - 5} more")
    
    if not clip_colors:
        print("Error: No clips were successfully analyzed!")
        return
    
    print(f"\nSuccessfully analyzed {len(clip_colors)} clips")
    
    if mode == "similarity":
        # Group similar colors together
        ordered_clips = []
        remaining_clips = list(clip_colors.keys())
        
        # Start with a random clip
        if remaining_clips:
            current_clip = remaining_clips.pop(0)
            ordered_clips.append(current_clip)
            
            # Find most similar clips
            with tqdm(total=len(remaining_clips), desc="Ordering clips") as pbar:
                while remaining_clips:
                    current_colors = clip_colors[current_clip]
                    min_distance = float('inf')
                    next_clip = None
                    
                    for clip in remaining_clips:
                        clip_cols = clip_colors[clip]
                        # Calculate minimum distance between any color pairs
                        distance = min(
                            color_distance(c1, c2)
                            for c1 in current_colors
                            for c2 in clip_cols
                        )
                        
                        if distance < min_distance:
                            min_distance = distance
                            next_clip = clip
                    
                    current_clip = next_clip
                    ordered_clips.append(current_clip)
                    remaining_clips.remove(next_clip)
                    pbar.update(1)
    
    else:  # transition mode
        target_colors = get_transition_target_colors(transition_type)
        if not target_colors:
            print(f"Invalid transition type: {transition_type}")
            return
        
        # Map clips to their closest target color
        clip_mapping = []
        for clip, colors in clip_colors.items():
            # Find the dominant color closest to any target color
            min_distance = float('inf')
            best_target_idx = 0
            
            for color in colors:
                for i, target in enumerate(target_colors):
                    distance = color_distance(color, target)
                    if distance < min_distance:
                        min_distance = distance
                        best_target_idx = i
            
            clip_mapping.append((clip, best_target_idx, min_distance))
        
        # Sort clips by target color index and then by distance
        clip_mapping.sort(key=lambda x: (x[1], x[2]))
        ordered_clips = [item[0] for item in clip_mapping]
    
    # Copy clips to output folder with new names
    if not ordered_clips:
        print("No clips to save! Check if color analysis succeeded.")
        return

    print("\nSaving ordered clips...")
    try:
        # Ensure output directory exists
        os.makedirs(output_folder, exist_ok=True)
        
        with tqdm(total=len(ordered_clips), desc="Saving clips") as pbar:
            for i, clip in enumerate(ordered_clips):
                try:
                    new_name = f'color_{i:04d}.mp4'
                    output_path = os.path.join(output_folder, new_name)
                    shutil.copy2(clip, output_path)
                    # Verify file was copied
                    if not os.path.exists(output_path):
                        print(f"Warning: Failed to save {new_name}")
                except Exception as e:
                    print(f"Error saving clip {clip}: {str(e)}")
                pbar.update(1)
        
        # Verify number of saved files
        saved_files = len(glob.glob(os.path.join(output_folder, 'color_????.mp4')))
        print(f"\nProcessed {len(ordered_clips)} clips")
        print(f"Successfully saved {saved_files} clips")
        print(f"Output saved to: {os.path.abspath(output_folder)}")
        
        if saved_files == 0:
            print("WARNING: No files were saved! Check file permissions and disk space.")
            
    except Exception as e:
        print(f"Error during file saving: {str(e)}")

if __name__ == "__main__":
    # Command line testing
    input_folder = input("Enter input folder path: ")
    output_folder = input("Enter output folder name: ")
    mode = input("Enter mode (similarity/transition): ")
    
    if mode == "transition":
        print("\nAvailable transitions:")
        print("1. rainbow")
        print("2. sunset")
        print("3. ocean")
        transition_type = input("Enter transition type: ")
    else:
        transition_type = None
    
    color_based_shuffle(input_folder, output_folder, mode, transition_type)