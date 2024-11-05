import os
import random
import string
import glob
import shutil
from pathlib import Path
from tqdm import tqdm
import psutil
import time
from datetime import datetime
import librosa
import av

def get_valid_folder(prompt, must_exist=True):
    """Get and validate folder path from user"""
    while True:
        folder = input(prompt).strip()
        if must_exist:
            if not os.path.exists(folder):
                print(f"Error: Folder '{folder}' not found!")
                continue
            if not os.path.isdir(folder):
                print(f"Error: '{folder}' is not a directory!")
                continue
            if not glob.glob(os.path.join(folder, 'clip_????.mp4')):
                print(f"Error: No clips found in '{folder}' matching pattern 'clip_XXXX.mp4'")
                continue
        return folder

def get_valid_audio_file(prompt):
    """Get and validate audio file path from user"""
    while True:
        audio_file = input(prompt).strip()
        if not os.path.exists(audio_file):
            print(f"Error: File '{audio_file}' not found!")
            continue
        if not audio_file.lower().endswith(('.mp3', '.wav')):
            print("Error: File must be .mp3 or .wav format!")
            continue
        return audio_file

def get_memory_usage():
    """Get current memory usage in MB"""
    process = psutil.Process()
    return process.memory_info().rss / (1024 * 1024)

def generate_hex_code(length=8):
    """Generate a random hex code of specified length"""
    hex_chars = string.hexdigits
    return ''.join(random.choice(hex_chars) for _ in range(length))

def get_video_duration(file_path):
    """Get duration of a video file using av"""
    try:
        with av.open(file_path) as container:
            duration = container.duration / av.time_base
            return duration
    except Exception as e:
        print(f"Error getting duration for {file_path}: {str(e)}")
        return 0

def get_total_clips_duration(folder):
    """Calculate total duration of all clips in folder"""
    clips = glob.glob(os.path.join(folder, 'clip_????.mp4'))
    total_duration = 0
    
    print("\nCalculating total duration of clips...")
    with tqdm(total=len(clips), desc="Processing") as pbar:
        for clip in clips:
            duration = get_video_duration(clip)
            total_duration += duration
            pbar.update(1)
    
    return total_duration

def calculate_reward_percentage(audio_duration, clips_duration):
    """Calculate reward percentage based on duration ratio"""
    if clips_duration == 0:
        return 0
    
    percentage = (audio_duration / clips_duration) * 100
    # Ensure percentage is between 1 and 100
    return max(1, min(100, percentage))

def auto_size_shuffle(input_folder, output_folder, audio_file):
    """Size-based reward shuffle with automatic percentage calculation"""
    clips = glob.glob(os.path.join(input_folder, 'clip_????.mp4'))
    
    # Get audio duration
    print("\nAnalyzing audio file duration...")
    try:
        audio_duration = librosa.get_duration(path=audio_file)
        print(f"Audio duration: {audio_duration:.2f} seconds")
    except Exception as e:
        print(f"Error analyzing audio file: {str(e)}")
        return
    
    # Get total clips duration
    clips_duration = get_total_clips_duration(input_folder)
    print(f"Total clips duration: {clips_duration:.2f} seconds")
    
    # Calculate reward percentage
    reward_percentage = calculate_reward_percentage(audio_duration, clips_duration)
    print(f"\nCalculated reward percentage: {reward_percentage:.1f}%")
    print(f"This will make the output match the audio duration of {audio_duration:.1f} seconds")
    
    print(f"\nFound {len(clips)} clips for size analysis")
    print(f"Initial memory usage: {get_memory_usage():.2f} MB")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Stage 1: Size Analysis
    print("\nStage 1: Analyzing and ordering by file size...")
    clip_sizes = []
    with tqdm(total=len(clips), desc="Analyzing files") as pbar:
        for clip in clips:
            size = os.path.getsize(clip)
            clip_sizes.append((clip, size))
            pbar.update(1)
    
    clip_sizes.sort(key=lambda x: x[1], reverse=True)
    
    # Stage 2: Renaming
    print("\nStage 2: Processing files by size order...")
    temp_dir = os.path.join(output_folder, "temp")
    os.makedirs(temp_dir, exist_ok=True)
    
    with tqdm(total=len(clip_sizes), desc="Processing files") as pbar:
        for i, (clip_path, size) in enumerate(clip_sizes, 1):
            try:
                size_mb = size / (1024 * 1024)
                new_path = os.path.join(temp_dir, f'size_{i:04d}_{size_mb:.2f}mb.mp4')
                shutil.copy2(clip_path, new_path)
                pbar.update(1)
                
                if i % 100 == 0:
                    current_mem = get_memory_usage()
                    pbar.set_postfix({"Memory (MB)": f"{current_mem:.1f}"})
                    
            except Exception as e:
                print(f"\nError processing {clip_path}: {str(e)}")
    
    # Stage 3: Selecting and Processing Reward Files
    print(f"\nStage 3: Selecting top {reward_percentage:.1f}% clips...")
    num_keep = int(len(clips) * (reward_percentage / 100))
    reward_clips = glob.glob(os.path.join(temp_dir, 'size_*.mp4'))[:num_keep]
    
    # Final stage: Rename with hex codes
    print("\nStage 4: Applying final names to reward clips...")
    used_codes = set()
    
    with tqdm(total=len(reward_clips), desc="Finalizing clips") as pbar:
        for i, clip_path in enumerate(reward_clips, 1):
            try:
                while True:
                    new_code = generate_hex_code()
                    if new_code not in used_codes:
                        used_codes.add(new_code)
                        break
                
                new_path = os.path.join(output_folder, f'reward_{new_code}.mp4')
                shutil.move(clip_path, new_path)
                pbar.update(1)
                
                if i % 50 == 0:
                    current_mem = get_memory_usage()
                    pbar.set_postfix({"Memory (MB)": f"{current_mem:.1f}"})
                    
            except Exception as e:
                print(f"\nError processing {clip_path}: {str(e)}")

    # Cleanup
    try:
        shutil.rmtree(temp_dir)
    except Exception as e:
        print(f"\nWarning: Could not remove temporary directory: {str(e)}")

    print(f"\nFinal memory usage: {get_memory_usage():.2f} MB")

def main():
    start_time = time.time()
    print(f"Beat-Synchronized Auto Shuffle v1.0 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=========================")
    print(f"System Memory: {psutil.virtual_memory().total / (1024**3):.1f} GB")
    print(f"Available Memory: {psutil.virtual_memory().available / (1024**3):.1f} GB")
    print("=========================")
    
    # Get audio file
    print("\nAudio File Selection")
    print("Please enter the path to the audio file (.mp3 or .wav)")
    audio_file = get_valid_audio_file("Enter audio file path: ")
    
    # Get input folder
    print("\nInput Folder Selection")
    print("Please enter the folder containing the clips to shuffle")
    print("(This folder should contain files named 'clip_XXXX.mp4')")
    input_folder = get_valid_folder("Enter input folder path: ")
    
    # Get output folder
    print("\nOutput Folder Selection")
    print("Please enter a name for the output folder")
    output_folder = input("Enter output folder name: ").strip()
    
    print("\nStarting automatic size-reward shuffle...")
    auto_size_shuffle(input_folder, output_folder, audio_file)
    
    elapsed_time = time.time() - start_time
    print(f"\nOperation complete! Total time: {elapsed_time:.1f} seconds")
    print(f"Output saved to: {os.path.abspath(output_folder)}")
    print("\nPress Enter to exit...")
    input()

if __name__ == "__main__":
    main()
