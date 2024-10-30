import torch
import av
import os
from pathlib import Path
from tqdm import tqdm
import numpy as np
from fractions import Fraction

def get_output_folder(input_file):
    """Create output folder based on input filename"""
    # Get filename without extension
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    # Create folder path
    output_dir = os.path.join(os.path.dirname(input_file), base_name)
    # Create directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

def split_video_cuda(input_file, segment_duration=2):
    """
    Split a video file into segments using GPU acceleration.
    
    Args:
        input_file (str): Path to input video file
        segment_duration (int): Duration of each segment in seconds
    """
    print(f"\nInitializing with parameters:")
    print(f"Input file: {input_file}")
    print(f"Segment duration: {segment_duration} seconds")

    if not torch.cuda.is_available():
        print("WARNING: CUDA not available. Falling back to CPU processing.")
    else:
        print(f"Using GPU: {torch.cuda.get_device_name(0)}")

    # Create output directory based on input filename
    output_dir = get_output_folder(input_file)
    print(f"Output directory: {output_dir}")

    try:
        # Open the video file
        print(f"\nOpening video file...")
        container = av.open(input_file)
        stream = container.streams.video[0]
        
        # Get video parameters
        fps = float(stream.average_rate)
        fps_fraction = Fraction(fps).limit_denominator()
        total_frames = stream.frames
        frames_per_segment = int(fps * segment_duration)
        
        print(f"Video information:")
        print(f"- FPS: {fps} ({fps_fraction.numerator}/{fps_fraction.denominator})")
        print(f"- Total frames: {total_frames}")
        print(f"- Frames per segment: {frames_per_segment}")
        print(f"- Estimated number of segments: {total_frames // frames_per_segment}")

        # Pre-calculate number of segments
        num_segments = total_frames // frames_per_segment
        
        # Create a CUDA stream for parallel processing
        cuda_stream = torch.cuda.Stream() if torch.cuda.is_available() else None
        
        # Process segments
        current_segment = []
        current_segment_idx = 0
        
        print("\nStarting video processing...")
        with tqdm(total=total_frames) as pbar:
            for frame in container.decode(video=0):
                current_segment.append(frame)
                
                if len(current_segment) == frames_per_segment:
                    output_path = os.path.join(output_dir, f'clip_{current_segment_idx:04d}.mp4')
                    
                    try:
                        # Process segment with GPU if available
                        if torch.cuda.is_available():
                            with torch.cuda.stream(cuda_stream):
                                # Convert frames to tensor and move to GPU
                                frames_tensor = torch.stack([
                                    torch.from_numpy(frame.to_ndarray(format='rgb24')).cuda()
                                    for frame in current_segment
                                ])
                                
                                # Process frames (potential for additional GPU-based processing here)
                                processed_frames = frames_tensor.cpu().numpy()
                        else:
                            processed_frames = np.stack([
                                frame.to_ndarray(format='rgb24')
                                for frame in current_segment
                            ])

                        # Write processed segment
                        output_container = av.open(output_path, mode='w')
                        stream = output_container.add_stream('h264', rate=fps_fraction)
                        stream.width = current_segment[0].width
                        stream.height = current_segment[0].height
                        stream.pix_fmt = 'yuv420p'
                        
                        for processed_frame in processed_frames:
                            frame = av.VideoFrame.from_ndarray(processed_frame, format='rgb24')
                            packet = stream.encode(frame)
                            output_container.mux(packet)

                        # Flush stream
                        packet = stream.encode(None)
                        output_container.mux(packet)
                        output_container.close()

                    except Exception as e:
                        print(f"\nError processing segment {current_segment_idx}: {str(e)}")
                        continue

                    # Clear segment and update counter
                    current_segment = []
                    current_segment_idx += 1
                
                pbar.update(1)

        print(f"\nCreated {current_segment_idx} clips in folder: {output_dir}")
        print("Processing complete!")

    except Exception as e:
        print(f"\nError processing video: {str(e)}")
        print("Error details:")
        print(f"- File: {input_file}")
        print(f"- Duration: {segment_duration}")
        raise

if __name__ == "__main__":
    print("CUDA Video Splitter v1.0")
    print("========================")
    
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"CUDA Version: {torch.version.cuda}")
    else:
        print("WARNING: CUDA not available. Will use CPU processing.")
    
    print("========================")
    
    # Get filename with error checking
    while True:
        filename = input("Enter the video filename: ").strip()
        if os.path.exists(filename):
            break
        print(f"Error: File '{filename}' not found! Please try again.")
    
    # Get duration with error checking
    while True:
        try:
            duration_input = input("Enter clip duration in seconds (default: 2): ").strip()
            if duration_input == "":
                duration = 2
                break
            duration = int(duration_input)
            if duration > 0:
                break
            print("Duration must be greater than 0.")
        except ValueError:
            print("Please enter a valid number.")
    
    print(f"\nStarting processing with:")
    print(f"- File: {filename}")
    print(f"- Duration: {duration} seconds")
    
    try:
        split_video_cuda(filename, duration)
    except Exception as e:
        print(f"\nFatal error: {str(e)}")
        print("Please check the error messages above for details.")
    
    print("\nPress Enter to exit...")
    input()