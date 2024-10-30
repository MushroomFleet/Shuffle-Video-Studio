import os
from moviepy.editor import VideoFileClip, concatenate_videoclips
from tqdm import tqdm
import time
from datetime import datetime

def get_valid_folder(prompt):
    """Get and validate folder path from user"""
    while True:
        folder = input(prompt).strip()
        if not os.path.exists(folder):
            print(f"Error: Folder '{folder}' not found!")
            continue
        if not os.path.isdir(folder):
            print(f"Error: '{folder}' is not a directory!")
            continue
        # Check for mp4 files
        mp4_files = [f for f in os.listdir(folder) if f.endswith('.mp4')]
        if not mp4_files:
            print(f"Error: No MP4 files found in '{folder}'")
            continue
        return folder

def join_videos(input_folder):
    """Join all MP4 files in the input folder"""
    # Create output directory
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Get list of all MP4 files
    video_files = [f for f in os.listdir(input_folder) if f.endswith('.mp4')]
    video_files.sort()  # Sort files to ensure consistent order
    
    if not video_files:
        print("No MP4 files found in the input folder!")
        return
    
    print(f"\nFound {len(video_files)} video files to join")
    print("Loading videos...")
    
    # Load all video clips with progress bar
    clips = []
    failed_clips = []
    
    with tqdm(total=len(video_files), desc="Loading clips") as pbar:
        for video_file in video_files:
            try:
                file_path = os.path.join(input_folder, video_file)
                clip = VideoFileClip(file_path)
                clips.append(clip)
                pbar.update(1)
            except Exception as e:
                print(f"\nError loading {video_file}: {str(e)}")
                failed_clips.append(video_file)
                pbar.update(1)
    
    if failed_clips:
        print(f"\nWarning: Failed to load {len(failed_clips)} clips:")
        for failed in failed_clips:
            print(f"- {failed}")
    
    if not clips:
        print("No clips were successfully loaded!")
        return
    
    print(f"\nSuccessfully loaded {len(clips)} clips")
    print("Joining videos...")
    
    try:
        # Generate output filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(output_dir, f"joined_video_{timestamp}.mp4")
        
        # Join clips
        final_clip = concatenate_videoclips(clips, method="compose")
        
        # Write final video
        print("\nWriting final video...")
        final_clip.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            verbose=False,
            logger=None
        )
        
        # Clean up
        final_clip.close()
        for clip in clips:
            clip.close()
        
        print(f"\nSuccessfully created: {output_path}")
        print(f"Output file size: {os.path.getsize(output_path) / (1024*1024):.1f} MB")
        
    except Exception as e:
        print(f"\nError joining videos: {str(e)}")
        # Clean up on error
        for clip in clips:
            try:
                clip.close()
            except:
                pass

def main():
    print("Shuffle Joiner v1.0")
    print("===================")
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("===================")
    
    print("\nInput Folder Selection")
    print("Please enter the folder containing the MP4 files to join")
    input_folder = get_valid_folder("Enter input folder path: ")
    
    start_time = time.time()
    join_videos(input_folder)
    
    elapsed_time = time.time() - start_time
    print(f"\nOperation complete! Total time: {elapsed_time:.1f} seconds")
    print("\nPress Enter to exit...")
    input()

if __name__ == "__main__":
    main()
import os
from moviepy.editor import VideoFileClip, concatenate_videoclips
from tqdm import tqdm
import time
from datetime import datetime

def get_valid_folder(prompt):
    """Get and validate folder path from user"""
    while True:
        folder = input(prompt).strip()
        if not os.path.exists(folder):
            print(f"Error: Folder '{folder}' not found!")
            continue
        if not os.path.isdir(folder):
            print(f"Error: '{folder}' is not a directory!")
            continue
        # Check for mp4 files
        mp4_files = [f for f in os.listdir(folder) if f.endswith('.mp4')]
        if not mp4_files:
            print(f"Error: No MP4 files found in '{folder}'")
            continue
        return folder

def join_videos(input_folder):
    """Join all MP4 files in the input folder"""
    # Create output directory
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Get list of all MP4 files
    video_files = [f for f in os.listdir(input_folder) if f.endswith('.mp4')]
    video_files.sort()  # Sort files to ensure consistent order
    
    if not video_files:
        print("No MP4 files found in the input folder!")
        return
    
    print(f"\nFound {len(video_files)} video files to join")
    print("Loading videos...")
    
    # Load all video clips with progress bar
    clips = []
    failed_clips = []
    
    with tqdm(total=len(video_files), desc="Loading clips") as pbar:
        for video_file in video_files:
            try:
                file_path = os.path.join(input_folder, video_file)
                clip = VideoFileClip(file_path)
                clips.append(clip)
                pbar.update(1)
            except Exception as e:
                print(f"\nError loading {video_file}: {str(e)}")
                failed_clips.append(video_file)
                pbar.update(1)
    
    if failed_clips:
        print(f"\nWarning: Failed to load {len(failed_clips)} clips:")
        for failed in failed_clips:
            print(f"- {failed}")
    
    if not clips:
        print("No clips were successfully loaded!")
        return
    
    print(f"\nSuccessfully loaded {len(clips)} clips")
    print("Joining videos...")
    
    try:
        # Generate output filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(output_dir, f"joined_video_{timestamp}.mp4")
        
        # Join clips
        final_clip = concatenate_videoclips(clips, method="compose")
        
        # Write final video
        print("\nWriting final video...")
        final_clip.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            verbose=False,
            logger=None
        )
        
        # Clean up
        final_clip.close()
        for clip in clips:
            clip.close()
        
        print(f"\nSuccessfully created: {output_path}")
        print(f"Output file size: {os.path.getsize(output_path) / (1024*1024):.1f} MB")
        
    except Exception as e:
        print(f"\nError joining videos: {str(e)}")
        # Clean up on error
        for clip in clips:
            try:
                clip.close()
            except:
                pass

def main():
    print("Shuffle Joiner v1.0")
    print("===================")
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("===================")
    
    print("\nInput Folder Selection")
    print("Please enter the folder containing the MP4 files to join")
    input_folder = get_valid_folder("Enter input folder path: ")
    
    start_time = time.time()
    join_videos(input_folder)
    
    elapsed_time = time.time() - start_time
    print(f"\nOperation complete! Total time: {elapsed_time:.1f} seconds")
    print("\nPress Enter to exit...")
    input()

if __name__ == "__main__":
    main()