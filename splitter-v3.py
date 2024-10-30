from moviepy.editor import VideoFileClip
import os

def get_valid_integer(prompt, min_value=1, max_value=3600):
    """
    Get a valid integer input from the user within specified range.
    
    Args:
        prompt (str): Message to display to user
        min_value (int): Minimum acceptable value
        max_value (int): Maximum acceptable value
    """
    while True:
        try:
            value = int(input(prompt))
            if min_value <= value <= max_value:
                return value
            print(f"Please enter a number between {min_value} and {max_value}")
        except ValueError:
            print("Please enter a valid number")

def split_video(input_file, segment_duration):
    """
    Split a video file into segments of specified duration.
    
    Args:
        input_file (str): Path to input video file
        segment_duration (int): Duration of each segment in seconds
    """
    # Check if file exists
    if not os.path.exists(input_file):
        print(f"Error: File '{input_file}' not found!")
        return
        
    # Create output directory if it doesn't exist
    output_dir = 'split_clips'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    try:
        # Load the video file
        print(f"Loading video: {input_file}")
        video = VideoFileClip(input_file)
        
        # Calculate number of segments
        total_duration = int(video.duration)
        num_segments = total_duration // segment_duration
        
        print(f"Total video duration: {total_duration} seconds")
        print(f"Creating {num_segments} clips of {segment_duration} seconds each...")
        
        # Split the video
        for i in range(num_segments):
            start_time = i * segment_duration
            segment = video.subclip(start_time, start_time + segment_duration)
            
            # Generate output filename
            output_filename = os.path.join(output_dir, f'clip_{i:04d}.mp4')
            
            # Write segment to file
            segment.write_videofile(output_filename, 
                                  codec='libx264', 
                                  audio_codec='aac',
                                  verbose=False,
                                  logger=None)
            
            # Show progress
            if (i + 1) % 10 == 0:
                print(f"Processed {i + 1}/{num_segments} clips")
                
        video.close()
        print("Splitting complete!")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        if 'video' in locals():
            video.close()

if __name__ == "__main__":
    print("Video Splitter v3.0")
    print("Place your video file in the same folder as this script.")
    print("=====================================")
    
    # Get filename from user
    filename = input("Enter the video filename (e.g., video.mp4): ").strip()
    
    # Get segment duration from user
    print("\nHow long should each clip be?")
    duration = get_valid_integer("Enter duration in seconds (1-3600): ")
    
    # Run the splitter
    split_video(filename, segment_duration=duration)
    
    print("\nPress Enter to exit...")
    input()
