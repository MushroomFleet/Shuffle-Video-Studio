import torch
import av
import os
import librosa
import numpy as np
from pathlib import Path
from tqdm import tqdm
from fractions import Fraction
import shutil
import math

def get_output_folder(input_file):
    """Create output folder based on input filename"""
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    output_dir = os.path.join(os.path.dirname(input_file), base_name)
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

def get_video_settings(input_video):
    """Get video settings from input file"""
    try:
        with av.open(input_video) as container:
            video_stream = container.streams.video[0]
            settings = {
                'width': video_stream.width,
                'height': video_stream.height,
                'pix_fmt': video_stream.pix_fmt,
                'fps': float(video_stream.average_rate),
                'codec_name': video_stream.codec_context.name,
                'duration': float(container.duration) / av.time_base if container.duration else None,
            }
            
            # Optional parameters - only add if available
            if hasattr(video_stream, 'bit_rate') and video_stream.bit_rate is not None:
                settings['bit_rate'] = video_stream.bit_rate
            
            return settings
    except Exception as e:
        print(f"Error reading video settings: {e}")
        return None

def detect_beats_and_bars(audio_file):
    """Detect beats and organize them into bars."""
    print("\nAnalyzing audio for beat and bar detection...")
    
    try:
        # Load audio file
        y, sr = librosa.load(audio_file)
        
        # Get tempo and beat frames
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr, units='frames')
        beat_times = librosa.frames_to_time(beat_frames, sr=sr)
        
        # Estimate time signature
        beats_per_bar = 4  # Default to 4/4 time
        
        # Group beats into bars
        num_beats = len(beat_times)
        num_complete_bars = num_beats // beats_per_bar
        
        # Create bar markers
        bar_times = []
        for i in range(num_complete_bars):
            bar_idx = i * beats_per_bar
            bar_times.append(beat_times[bar_idx])
        
        tempo_value = tempo.item() if hasattr(tempo, 'item') else float(tempo)
        
        print(f"Detected tempo: {tempo_value:.1f} BPM")
        print(f"Time signature: {beats_per_bar}/4")
        print(f"Found {num_beats} beats")
        print(f"Grouped into {len(bar_times)} complete bars")
        
        return bar_times, tempo_value, beats_per_bar
        
    except Exception as e:
        print(f"Error during beat/bar detection: {str(e)}")
        raise

def get_bar_multiplier():
    """Get user input for number of bars per segment"""
    while True:
        print("\nSelect bars per segment:")
        print("1. Single bar (4 beats)")
        print("2. Two bars (8 beats)")
        print("3. Four bars (16 beats)")
        print("4. Eight bars (32 beats)")
        
        try:
            choice = int(input("Enter your choice (1-4): "))
            if 1 <= choice <= 4:
                bars = {1: 1, 2: 2, 3: 4, 4: 8}[choice]
                return bars
            print("Please enter a number between 1 and 4")
        except ValueError:
            print("Please enter a valid number")

def process_frame_batch(frames, device='cuda'):
    """Process a batch of frames with memory management"""
    try:
        processed = []
        for frame in frames:
            array = frame.to_ndarray(format='rgb24')
            tensor = torch.from_numpy(array)
            if device == 'cuda':
                tensor = tensor.cuda()
            processed.append(tensor)
            del array

        if processed:
            stacked = torch.stack(processed)
            result = stacked.cpu().numpy()
            del stacked
            del processed
            torch.cuda.empty_cache()
            return result
        return None
    except Exception as e:
        print(f"Error processing frame batch: {e}")
        return None

def write_video_segment(frames, output_path, fps_fraction, video_settings):
    """Write video frames to a file using matched settings from input"""
    try:
        with av.open(output_path, mode='w') as container:
            stream = container.add_stream('h264', rate=fps_fraction)
            
            # Match input video parameters
            stream.width = video_settings['width']
            stream.height = video_settings['height']
            stream.pix_fmt = video_settings['pix_fmt']
            
            if 'bit_rate' in video_settings and video_settings['bit_rate']:
                stream.bit_rate = video_settings['bit_rate']
            
            # Set encoding options
            stream.codec_context.options = {
                'crf': '23',
                'preset': 'medium',
                'profile:v': 'high',
                'level:v': '4.1',
                'g': '12',
                'bf': '2',
                'threads': '0'
            }
            
            # Write frames
            for frame_data in frames:
                frame = av.VideoFrame.from_ndarray(frame_data, format='rgb24')
                for packet in stream.encode(frame):
                    container.mux(packet)
            
            # Flush the stream
            for packet in stream.encode():
                container.mux(packet)
                
        return True
    except Exception as e:
        print(f"Error writing video segment: {e}")
        return False

def extract_segment_frames(container, start_time, duration, fps):
    """Extract frames for a specific time segment"""
    try:
        # Get video stream
        stream = container.streams.video[0]
        
        # Calculate frame positions
        start_pts = int(start_time * stream.time_base.denominator / stream.time_base.numerator)
        end_pts = int((start_time + duration) * stream.time_base.denominator / stream.time_base.numerator)
        
        # Seek to the start position
        container.seek(start_pts, stream=stream)
        
        frames = []
        for frame in container.decode(video=0):
            if frame.pts >= end_pts:
                break
            if frame.pts >= start_pts:
                frames.append(frame)
        
        return frames
    except Exception as e:
        print(f"Error extracting frames: {str(e)}")
        return []

def split_video_on_bars(input_video, input_audio, bars_per_segment):
    """Split video into bar-synchronized segments"""
    print(f"\nInitializing bar-synchronized video splitter:")
    print(f"Input video: {input_video}")
    print(f"Input audio: {input_audio}")
    print(f"Bars per segment: {bars_per_segment}")

    if torch.cuda.is_available():
        print(f"Using GPU: {torch.cuda.get_device_name(0)}")
        total_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        print(f"Total GPU Memory: {total_memory:.2f} GB")
        torch.cuda.empty_cache()
    else:
        print("WARNING: CUDA not available. Falling back to CPU processing.")

    output_dir = get_output_folder(input_video)
    print(f"Output directory: {output_dir}")

    try:
        # Get video settings
        video_settings = get_video_settings(input_video)
        if not video_settings:
            raise Exception("Failed to read input video settings")
            
        print("\nVideo settings from input:")
        for key, value in video_settings.items():
            print(f"- {key}: {value}")

        # Get video duration
        video_duration = video_settings['duration']
        if not video_duration:
            raise Exception("Could not determine video duration")

        # Get bar timings
        bar_times, tempo, beats_per_bar = detect_beats_and_bars(input_audio)
        
        # Open video and get parameters
        container = av.open(input_video)
        video_stream = container.streams.video[0]
        fps = float(video_stream.average_rate)
        fps_fraction = Fraction(fps).limit_denominator()
        
        # Calculate timing information
        seconds_per_beat = 60 / tempo
        seconds_per_bar = seconds_per_beat * 4
        segment_duration = seconds_per_bar * bars_per_segment
        
        print(f"\nTiming calculations:")
        print(f"- Video duration: {video_duration:.3f} seconds")
        print(f"- Tempo: {tempo:.1f} BPM")
        print(f"- Seconds per beat: {seconds_per_beat:.3f}")
        print(f"- Seconds per bar: {seconds_per_bar:.3f}")
        print(f"- Segment duration: {segment_duration:.3f} seconds")
        
        # Calculate total number of segments based on video duration
        total_segments = math.ceil(video_duration / segment_duration)
        
        # Create segment time markers
        segments = []
        current_time = 0
        for i in range(total_segments):
            segments.append((current_time, segment_duration))
            current_time += segment_duration
        
        print(f"\nSplitting into {len(segments)} segments")
        print(f"Each segment is {bars_per_segment} bars ({bars_per_segment * beats_per_bar} beats)")
        
        # Process segments
        max_batch_size = 30
        
        with tqdm(total=len(segments), desc="Processing segments") as pbar:
            for segment_idx, (start_time, duration) in enumerate(segments):
                output_path = os.path.join(output_dir, f'clip_{segment_idx:04d}.mp4')
                
                try:
                    # Extract frames for this segment
                    segment_frames = extract_segment_frames(container, start_time, duration, fps)
                    
                    if not segment_frames:
                        print(f"\nWarning: No frames extracted for segment {segment_idx}")
                        continue
                    
                    # Process frames in batches
                    processed_frames = []
                    for i in range(0, len(segment_frames), max_batch_size):
                        batch = segment_frames[i:i + max_batch_size]
                        frames = process_frame_batch(batch)
                        if frames is not None:
                            processed_frames.extend(frames)
                    
                    # Write processed frames to video
                    if processed_frames:
                        success = write_video_segment(processed_frames, output_path, fps_fraction, video_settings)
                        if not success:
                            print(f"\nWarning: Failed to write segment {segment_idx}")
                    
                    print(f"\nSegment {segment_idx}: Processed {len(segment_frames)} frames")
                    
                    # Clear processed frames to free memory
                    del processed_frames
                    del segment_frames
                    torch.cuda.empty_cache()
                    
                except Exception as e:
                    print(f"\nError processing segment {segment_idx}: {str(e)}")
                    continue
                
                pbar.update(1)
        
        print(f"\nProcessed {len(segments)} clips")
        print(f"Output directory: {output_dir}")
        print("Processing complete!")

    except Exception as e:
        print(f"\nError processing video: {str(e)}")
        print(f"Video: {input_video}")
        print(f"Audio: {input_audio}")
        raise
    finally:
        if 'container' in locals():
            container.close()
        torch.cuda.empty_cache()

if __name__ == "__main__":
    print("Bar-Synchronized CUDA Video Splitter v2.0")
    print("=========================================")
    
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"CUDA Version: {torch.version.cuda}")
    else:
        print("WARNING: CUDA not available. Will use CPU processing.")
    
    print("=========================================")
    
    # Get input files
    while True:
        video_filename = input("Enter the video filename: ").strip()
        if os.path.exists(video_filename):
            break
        print(f"Error: File '{video_filename}' not found!")
    
    while True:
        audio_filename = input("Enter the audio filename (.mp3 or .wav): ").strip()
        if os.path.exists(audio_filename):
            if audio_filename.lower().endswith(('.mp3', '.wav')):
                break
            print("Error: File must be .mp3 or .wav format!")
            continue
        print(f"Error: File '{audio_filename}' not found!")
    
    # Get bar multiplier
    bar_multiplier = get_bar_multiplier()
    
    print(f"\nStarting processing with:")
    print(f"- Video: {video_filename}")
    print(f"- Audio: {audio_filename}")
    print(f"- Bars per segment: {bar_multiplier}")
    
    try:
        split_video_on_bars(video_filename, audio_filename, bar_multiplier)
    except Exception as e:
        print(f"\nFatal error: {str(e)}")
        print("Please check the error messages above for details.")
    
    print("\nPress Enter to exit...")
    input()