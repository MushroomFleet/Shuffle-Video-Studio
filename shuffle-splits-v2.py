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
from color_shuffle import color_based_shuffle  # Import the new color shuffling module

def print_shuffle_help():
    """Print detailed help information about shuffle modes"""
    print("\nShuffle Mode Details:")
    print("=====================")
    print("\n1. Simple Shuffle")
    print("   - Randomly renames clips with hex codes")
    print("   - Fast and memory-efficient")
    print("   - Good for basic randomization")
    
    print("\n2. Size Reward Shuffle")
    print("   - Analyzes file sizes to identify high-quality clips")
    print("   - Keeps a specified percentage of larger files")
    print("   - Best for quality-based selection")
    
    print("\n3. Color Similarity Shuffle")
    print("   - Groups clips with similar color palettes")
    print("   - Analyzes dominant colors in each clip")
    print("   - Creates visually cohesive sequences")
    print("   - Good for artistic/aesthetic arrangements")
    
    print("\n4. Color Transition Shuffle")
    print("   - Creates smooth color transitions")
    print("   - Available transitions:")
    print("     * Rainbow: Full spectrum color progression")
    print("     * Sunset: Warm orange to cool purple transition")
    print("     * Ocean: Light to deep blue progression")
    print("   - Best for creating visual narratives")
    
    print("\nNote: Color-based modes require more processing time")

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

def get_memory_usage():
    """Get current memory usage in MB"""
    process = psutil.Process()
    return process.memory_info().rss / (1024 * 1024)

def generate_hex_code(length=8):
    """Generate a random hex code of specified length"""
    hex_chars = string.hexdigits
    return ''.join(random.choice(hex_chars) for _ in range(length))

def get_valid_percentage():
    """Get valid percentage input from user"""
    while True:
        try:
            percentage = float(input("\nEnter reward percentage (1-100): "))
            if 1 <= percentage <= 100:
                return percentage
            print("Please enter a number between 1 and 100")
        except ValueError:
            print("Please enter a valid number")

def simple_shuffle(input_folder, output_folder):
    """Original hex-based shuffle method"""
    clips = glob.glob(os.path.join(input_folder, 'clip_????.mp4'))
    
    print(f"Found {len(clips)} clips to shuffle")
    print(f"Initial memory usage: {get_memory_usage():.2f} MB")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    start_time = time.time()
    used_codes = set()
    
    # Using tqdm for progress bar
    with tqdm(total=len(clips), desc="Shuffling clips") as pbar:
        for i, clip_path in enumerate(clips, 1):
            try:
                while True:
                    new_code = generate_hex_code()
                    if new_code not in used_codes:
                        used_codes.add(new_code)
                        break
                
                new_path = os.path.join(output_folder, f'shuffle_{new_code}.mp4')
                shutil.copy2(clip_path, new_path)
                pbar.update(1)
                
                # Memory check every 100 files
                if i % 100 == 0:
                    current_mem = get_memory_usage()
                    pbar.set_postfix({"Memory (MB)": f"{current_mem:.1f}"})
                    
            except Exception as e:
                print(f"\nError processing {clip_path}: {str(e)}")

    elapsed_time = time.time() - start_time
    print(f"\nProcessing complete in {elapsed_time:.1f} seconds")
    print(f"Final memory usage: {get_memory_usage():.2f} MB")

def size_reward_shuffle(input_folder, output_folder):
    """Size-based reward shuffle method with progress bars and memory optimization"""
    clips = glob.glob(os.path.join(input_folder, 'clip_????.mp4'))
    
    reward_percentage = get_valid_percentage()
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
    print(f"\nStage 3: Selecting top {reward_percentage}% clips...")
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
    print(f"Split Clips Shuffler v2.1 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=========================")
    print(f"System Memory: {psutil.virtual_memory().total / (1024**3):.1f} GB")
    print(f"Available Memory: {psutil.virtual_memory().available / (1024**3):.1f} GB")
    print("=========================")
    
    # Show help text
    print("\nWould you like to see detailed information about shuffle modes?")
    if input("Show help? (y/n): ").lower().strip() == 'y':
        print_shuffle_help()
    
    # Get input folder
    print("\nInput Folder Selection")
    print("Please enter the folder containing the clips to shuffle")
    print("(This folder should contain files named 'clip_XXXX.mp4')")
    input_folder = get_valid_folder("Enter input folder path: ")
    
    # Get output folder
    print("\nOutput Folder Selection")
    print("Please enter a name for the output folder")
    output_folder = input("Enter output folder name: ").strip()
    
    print("\nAvailable shuffle methods:")
    print("1. Simple Shuffle (Random hex renaming)")
    print("2. Size Reward Shuffle (Size-based analysis with customizable reward percentage)")
    print("3. Color Similarity Shuffle (Sort by dominant colors)")
    print("4. Color Transition Shuffle (Create smooth color transitions)")
    print("=========================")
    
    while True:
        try:
            choice = int(input("\nSelect shuffle method (1-4): "))
            if choice in [1, 2, 3, 4]:
                break
            print("Please enter a number between 1 and 4")
        except ValueError:
            print("Please enter a valid number")
    
    if choice == 1:
        print("\nExecuting Simple Shuffle...")
        simple_shuffle(input_folder, output_folder)
    elif choice == 2:
        print("\nExecuting Size Reward Shuffle...")
        size_reward_shuffle(input_folder, output_folder)
    elif choice == 3:
        print("\nExecuting Color Similarity Shuffle...")
        color_based_shuffle(input_folder, output_folder, mode="similarity")
    else:
        print("\nExecuting Color Transition Shuffle...")
        print("\nSelect transition type:")
        print("1. Rainbow")
        print("2. Sunset")
        print("3. Ocean")
        
        while True:
            try:
                transition_choice = int(input("\nSelect transition type (1-3): "))
                if transition_choice in [1, 2, 3]:
                    break
                print("Please enter a number between 1 and 3")
            except ValueError:
                print("Please enter a valid number")
        
        transition_types = {1: "rainbow", 2: "sunset", 3: "ocean"}
        color_based_shuffle(input_folder, output_folder, mode="transition", 
                          transition_type=transition_types[transition_choice])
    
    elapsed_time = time.time() - start_time
    print(f"\nOperation complete! Total time: {elapsed_time:.1f} seconds")
    print(f"Output saved to: {os.path.abspath(output_folder)}")
    print("\nPress Enter to exit...")
    input()

if __name__ == "__main__":
    main()