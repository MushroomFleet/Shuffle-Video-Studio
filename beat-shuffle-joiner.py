import os
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips
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

def get_valid_audio(prompt):
    """Get and validate audio file path"""
    while True:
        audio_file = input(prompt).strip()
        if not os.path.exists(audio_file):
            print(f"Error: File '{audio_file}' not found!")
            continue
        if not audio_file.lower().endswith(('.mp3', '.wav')):
            print("Error: File must be .mp3 or .wav format!")
            continue
        return audio_file

def join_videos_with_audio(input_folder, audio_file):
    """Join all MP4 files in the input folder and add audio"""
    # Create output directory
    output_dir = "beat-output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Get list of all MP4 files
    video_files = [f for f in os.listdir(input_folder) if f.endswith('.mp4')]
    video_files.sort()  # Sort files to ensure consistent order
    
    if not video_files:
        print("No MP4 files found in the input folder!")
        return
    
    print(f"\nFound {len(video_files)} video files to join")
    
    try:
        # Load audio file
        print("\nLoading audio file...")
        audio_clip = AudioFileClip(audio_file)
        audio_duration = audio_clip.duration
        print(f"Audio duration: {audio_duration:.2f} seconds")
        
        # Load all video clips with progress bar
        print("\nLoading video clips...")
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
        
        # Join clips
        print("\nJoining videos...")
        final_clip = concatenate_videoclips(clips, method="compose")
        video_duration = final_clip.duration
        
        print(f"\nVideo duration: {video_duration:.2f} seconds")
        print(f"Audio duration: {audio_duration:.2f} seconds")
        
        # Handle duration mismatch
        if video_duration > audio_duration:
            print(f"\nVideo ({video_duration:.2f}s) is longer than audio ({audio_duration:.2f}s)")
            print("Truncating video to match audio length")
            final_clip = final_clip.subclip(0, audio_duration)
        elif video_duration < audio_duration:
            print(f"Audio ({audio_duration:.2f}s) is longer than video ({video_duration:.2f}s)")
            print("Truncating audio to match video length")
            audio_clip = audio_clip.subclip(0, video_duration)
        
        # Add audio to video
        print("\nAdding audio to video...")
        final_clip = final_clip.set_audio(audio_clip)
        
        # Generate output filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(output_dir, f'beat_sync_video_{timestamp}.mp4')
        
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
        audio_clip.close()
        for clip in clips:
            clip.close()
        
        print(f"\nSuccessfully created: {output_path}")
        print(f"Output file size: {os.path.getsize(output_path) / (1024*1024):.1f} MB")
        
    except Exception as e:
        print(f"\nError joining videos: {str(e)}")
        # Clean up on error
        if 'audio_clip' in locals():
            audio_clip.close()
        if 'final_clip' in locals():
            final_clip.close()
        for clip in clips:
            try:
                clip.close()
            except:
                pass

def main():
    print("Beat Shuffle Joiner v1.0")
    print("========================")
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("========================")
    
    print("\nAudio File Selection")
    print("Please enter the path to the audio file (.mp3 or .wav)")
    audio_file = get_valid_audio("Enter audio file path: ")
    
    print("\nInput Folder Selection")
    print("Please enter the folder containing the MP4 files to join")
    input_folder = get_valid_folder("Enter input folder path: ")
    
    start_time = time.time()
    join_videos_with_audio(input_folder, audio_file)
    
    elapsed_time = time.time() - start_time
    print(f"\nOperation complete! Total time: {elapsed_time:.1f} seconds")
    print("\nPress Enter to exit...")
    input()

if __name__ == "__main__":
    main()