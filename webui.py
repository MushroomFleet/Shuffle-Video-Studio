import gradio as gr
import os
import torch
import librosa
import shutil
import importlib.util
from pathlib import Path
from datetime import datetime
from moviepy.editor import VideoFileClip, AudioFileClip
import sys
from io import StringIO

# Function to import python files with hyphens in their names
def import_hyphenated_file(filename):
    module_name = filename.replace('.py', '').replace('-', '_')
    spec = importlib.util.spec_from_file_location(module_name, filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Import all required modules using importlib
try:
    print("Loading modules...")
    video_splitter = import_hyphenated_file("video-splitter-cuda.py")
    print("- Loaded video splitter")
    beat_splitter = import_hyphenated_file("beat-splitter-cudaV2.py")
    print("- Loaded beat splitter")
    shuffle_splits = import_hyphenated_file("shuffle-splits-v2.py")
    print("- Loaded shuffle splits")
    shuffle_joiner = import_hyphenated_file("ShuffleJoiner.py")
    print("- Loaded shuffle joiner")
    beat_joiner = import_hyphenated_file("beat-shuffle-joiner.py")
    print("- Loaded beat joiner")
except Exception as e:
    print(f"Error loading modules: {str(e)}")
    raise

class InputSimulator:
    def __init__(self, inputs):
        self.inputs = inputs
        self.input_index = 0
        self.buffer = ""
    
    def __call__(self, prompt=""):
        if self.input_index < len(self.inputs):
            result = str(self.inputs[self.input_index]) + "\n"
            self.input_index += 1
            return result
        return "\n"
    
    def readline(self):
        if self.input_index < len(self.inputs):
            result = str(self.inputs[self.input_index]) + "\n"
            self.input_index += 1
            return result
        return "\n"

    def read(self, size=-1):
        if self.input_index < len(self.inputs):
            result = str(self.inputs[self.input_index]) + "\n"
            self.input_index += 1
            return result
        return "\n"

class VideoShuffleStudio:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.temp_dir = os.path.join(self.base_dir, "temp_processing")
        self.output_dir = os.path.join(self.base_dir, "output")
        os.makedirs(self.temp_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)

    def check_cuda(self):
        if torch.cuda.is_available():
            return f"GPU Available: {torch.cuda.get_device_name(0)}"
        return "CUDA not available. Using CPU processing."

    def create_permanent_file(self, temp_file, prefix):
        """Create a permanent copy of a temporary file with proper extension"""
        if temp_file is None:
            return None
        
        # Get the original file extension
        _, ext = os.path.splitext(temp_file.name)
        
        # Create a new filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_filename = f"{prefix}_{timestamp}{ext}"
        permanent_path = os.path.join(self.temp_dir, new_filename)
        
        # Copy the temporary file to permanent location
        shutil.copy2(temp_file.name, permanent_path)
        
        return permanent_path

    def process_standard_split(self, video_file, duration):
        if not video_file:
            return "No video file provided."
        
        try:
            # Create permanent copy of the uploaded file
            video_path = self.create_permanent_file(video_file, "input_video")
            print(f"Processing video: {video_path}")
            
            # Create output directory
            video_name = os.path.splitext(os.path.basename(video_path))[0]
            output_folder = os.path.join(self.output_dir, f"split_{video_name}")
            os.makedirs(output_folder, exist_ok=True)
            
            # Modify the video path to use the output directory
            # We need to patch the video_splitter's get_output_folder function behavior
            original_get_output_folder = video_splitter.get_output_folder
            
            def patched_get_output_folder(input_file):
                """Override to use our desired output folder"""
                return output_folder
            
            # Temporarily replace the function
            video_splitter.get_output_folder = patched_get_output_folder
            
            try:
                # Process the video
                print(f"Splitting video into {output_folder}")
                video_splitter.split_video_cuda(video_path, int(duration))
            finally:
                # Restore the original function
                video_splitter.get_output_folder = original_get_output_folder
            
            return f"Video split complete. Output in: {output_folder}"
        except Exception as e:
            return f"Error during video splitting: {str(e)}"

    def process_beat_split(self, video_file, audio_file, bars_per_segment):
        if not video_file or not audio_file:
            return "Both video and audio files are required."
        
        try:
            # Create permanent copies of the uploaded files in temp directory
            video_path = self.create_permanent_file(video_file, "input_video")
            audio_path = self.create_permanent_file(audio_file, "input_audio")
            
            print(f"Processing video: {video_path}")
            print(f"Using audio: {audio_path}")
            
            # Create output directory in the output folder
            video_name = os.path.splitext(os.path.basename(video_path))[0]
            output_folder = os.path.join(self.output_dir, f"beat_split_{video_name}")
            os.makedirs(output_folder, exist_ok=True)
            
            # Modify the video path to use the output directory
            # We need to patch the beat_splitter's get_output_folder function behavior
            original_get_output_folder = beat_splitter.get_output_folder
            
            def patched_get_output_folder(input_file):
                """Override to use our desired output folder"""
                return output_folder
            
            # Temporarily replace the function
            beat_splitter.get_output_folder = patched_get_output_folder
            
            try:
                # Process the video
                print(f"Splitting video into {output_folder}")
                beat_splitter.split_video_on_bars(video_path, audio_path, int(bars_per_segment))
            finally:
                # Restore the original function
                beat_splitter.get_output_folder = original_get_output_folder
            
            return f"Beat-synchronized splitting complete. Output in: {output_folder}"
        except Exception as e:
            return f"Error during beat splitting: {str(e)}"

    def process_shuffle(self, input_folder, shuffle_type, reward_percentage=None):
        if not input_folder:
            return "No input folder specified."
        
        try:
            # Create absolute path if relative path provided
            if not os.path.isabs(input_folder):
                input_folder = os.path.join(self.base_dir, input_folder)
            
            # Create output folder
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_folder = os.path.join(self.output_dir, f"shuffled_{timestamp}")
            os.makedirs(output_folder, exist_ok=True)
            
            print(f"Processing folder: {input_folder}")
            print(f"Output folder: {output_folder}")
            
            if shuffle_type == "simple":
                shuffle_splits.simple_shuffle(input_folder, output_folder)
            else:
                # Save the original stdin
                original_stdin = sys.stdin
                
                try:
                    # Create input simulator with the reward percentage
                    simulated_input = InputSimulator([float(reward_percentage)])
                    sys.stdin = simulated_input
                    
                    # Call the original function
                    shuffle_splits.size_reward_shuffle(input_folder, output_folder)
                finally:
                    # Restore original stdin
                    sys.stdin = original_stdin
            
            return f"Shuffle complete. Output in: {output_folder}"
        except Exception as e:
            # Make sure to restore stdin even if there's an error
            if 'original_stdin' in locals():
                sys.stdin = original_stdin
            return f"Error during shuffling: {str(e)}"

    def process_join(self, input_folder):
        if not input_folder:
            return "No input folder specified."
        
        try:
            # Create absolute path if relative path provided
            if not os.path.isabs(input_folder):
                input_folder = os.path.join(self.base_dir, input_folder)
            
            print(f"Processing folder: {input_folder}")
            shuffle_joiner.join_videos(input_folder)
            return "Video joining complete. Output in: output folder"
        except Exception as e:
            return f"Error during joining: {str(e)}"

    def process_beat_join(self, input_folder, audio_file):
        if not input_folder or not audio_file:
            return "Both input folder and audio file are required."
        
        try:
            # Create absolute path if relative path provided
            if not os.path.isabs(input_folder):
                input_folder = os.path.join(self.base_dir, input_folder)
            
            # Create permanent copy of the audio file
            audio_path = self.create_permanent_file(audio_file, "join_audio")
            
            print(f"Processing folder: {input_folder}")
            print(f"Using audio: {audio_path}")
            
            beat_joiner.join_videos_with_audio(input_folder, audio_path)
            return "Beat-synchronized joining complete. Output in: beat-output folder"
        except Exception as e:
            return f"Error during beat joining: {str(e)}"

def create_ui():
    vss = VideoShuffleStudio()
    
    with gr.Blocks(title="Video Shuffle Studio") as app:
        gr.Markdown("# Video Shuffle Studio")
        gr.Markdown(vss.check_cuda())
        
        with gr.Tabs():
            # Standard Split Tab
            with gr.Tab("Standard Split"):
                with gr.Row():
                    split_video = gr.File(label="Input Video")
                    split_duration = gr.Number(label="Clip Duration (seconds)", value=2, minimum=1)
                split_btn = gr.Button("Split Video")
                split_output = gr.Textbox(label="Output Status")
                
                split_btn.click(
                    fn=vss.process_standard_split,
                    inputs=[split_video, split_duration],
                    outputs=split_output
                )

            # Beat Split Tab
            with gr.Tab("Beat Split"):
                with gr.Row():
                    beat_video = gr.File(label="Input Video")
                    beat_audio = gr.File(label="Input Audio")
                    bars_per_segment = gr.Number(label="Bars per Segment", value=1, minimum=1)
                beat_split_btn = gr.Button("Split on Beats")
                beat_split_output = gr.Textbox(label="Output Status")
                
                beat_split_btn.click(
                    fn=vss.process_beat_split,
                    inputs=[beat_video, beat_audio, bars_per_segment],
                    outputs=beat_split_output
                )

            # Shuffle Tab
            with gr.Tab("Shuffle"):
                shuffle_folder = gr.Textbox(label="Input Folder Path")
                shuffle_type = gr.Radio(["simple", "size_reward"], label="Shuffle Type", value="simple")
                reward_percentage = gr.Slider(minimum=1, maximum=100, value=50, label="Reward Percentage")
                shuffle_btn = gr.Button("Shuffle Clips")
                shuffle_output = gr.Textbox(label="Output Status")
                
                shuffle_btn.click(
                    fn=vss.process_shuffle,
                    inputs=[shuffle_folder, shuffle_type, reward_percentage],
                    outputs=shuffle_output
                )

            # Join Tab
            with gr.Tab("Join"):
                join_folder = gr.Textbox(label="Input Folder Path")
                join_btn = gr.Button("Join Clips")
                join_output = gr.Textbox(label="Output Status")
                
                join_btn.click(
                    fn=vss.process_join,
                    inputs=[join_folder],
                    outputs=join_output
                )

            # Beat Join Tab
            with gr.Tab("Beat Join"):
                beat_join_folder = gr.Textbox(label="Input Folder Path")
                beat_join_audio = gr.File(label="Audio File")
                beat_join_btn = gr.Button("Join with Audio")
                beat_join_output = gr.Textbox(label="Output Status")
                
                beat_join_btn.click(
                    fn=vss.process_beat_join,
                    inputs=[beat_join_folder, beat_join_audio],
                    outputs=beat_join_output
                )

    return app

if __name__ == "__main__":
    app = create_ui()
    app.launch(
        server_name="127.0.0.1",  # Local only
        server_port=7860,
        share=False  # Disable public URL
    )