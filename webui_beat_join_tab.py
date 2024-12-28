import gradio as gr
import os
from pathlib import Path
import time
from functools import partial

def process_beat_join(input_folder, audio_file, vss_instance):
    """Process folder of clips for joining with audio synchronization"""
    if not input_folder or not audio_file:
        return "Both input folder and audio file are required."
    
    try:
        # Validate input folder
        valid, message = vss_instance.validate_input_folder(input_folder)
        if not valid:
            return message

        # Initialize progress tracking
        update_progress = vss_instance.get_progress_updater()
        start_time = time.time()
        messages = []  # Store all messages
        
        # Create permanent copy of audio file
        audio_path = vss_instance.create_permanent_file(audio_file, "join_audio")
        input_folder = vss_instance.resolve_folder_path(input_folder)
        
        messages.append(update_progress(f"Processing folder: {input_folder}"))
        messages.append(update_progress(f"Using audio: {os.path.basename(audio_path)}"))
        
        # Count input files
        input_files = list(Path(input_folder).glob("*.mp4"))
        messages.append(update_progress(f"Found {len(input_files)} clips to join"))
        
        # Create VideoFileWriter redirect for progress
        class ProgressRedirect:
            def __init__(self, update_fn):
                self.update_fn = update_fn
                self.buffer = []
                
            def write(self, text):
                if "t:" in text:  # Writing progress
                    messages.append(self.update_fn(f"Writing: {text.strip()}"))
                elif "clip" in text.lower():  # Loading clip
                    messages.append(self.update_fn(f"Loading: {text.strip()}"))
                elif "audio" in text.lower():  # Audio processing
                    messages.append(self.update_fn(f"Audio: {text.strip()}"))
                    
            def flush(self):
                pass

        # Redirect moviepy progress to our updater
        import sys
        original_stdout = sys.stdout
        sys.stdout = ProgressRedirect(update_progress)
        
        try:
            messages.append(update_progress("\nAnalyzing audio file..."))
            vss_instance.beat_joiner.join_videos_with_audio(input_folder, audio_path)
            
            # Get output file details
            output_dir = Path("beat-output")
            output_files = list(output_dir.glob("beat_sync_video_*.mp4"))
            if output_files:
                latest_output = max(output_files, key=lambda p: p.stat().st_mtime)
                size_mb = latest_output.stat().st_size / (1024 * 1024)
                
                processing_time = time.time() - start_time
                
                messages.append(update_progress("\nJoin complete!"))
                messages.append(update_progress(f"Time taken: {processing_time:.1f} seconds"))
                messages.append(update_progress(f"Output file: {latest_output.name}"))
                messages.append(update_progress(f"File size: {size_mb:.1f} MB"))
                messages.append(update_progress("\nOutput saved to beat-output folder"))
            else:
                messages.append(update_progress("\nWarning: No output file found!"))
                
        finally:
            # Restore stdout and clean up
            sys.stdout = original_stdout
            vss_instance.clean_temp_files(audio_path)
            
        return "\n".join(messages)
            
    except Exception as e:
        return vss_instance.process_error(e, "beat-synchronized joining")

def create_beat_join_tab(vss):
    """Create the beat-synchronized join tab interface"""
    with gr.Column():
        # Input folder selection
        beat_join_folder = gr.Textbox(
            label="Input Folder Path",
            placeholder="Enter path to folder containing clips"
        )
        
        # Audio file upload
        beat_join_audio = gr.File(
            label="Audio File",
            file_types=[".mp3", ".wav"],
            file_count="single"
        )
        
        # Add tips
        gr.Markdown("""
        **Audio Tips:**
        - Use high-quality audio files
        - MP3 or WAV format recommended
        - Audio will be synced with video length
        - Longer audio will be trimmed
        - Shorter audio will be extended
        """)
        
        # Add processing button
        beat_join_btn = gr.Button(
            value="Join with Audio",
            variant="primary"
        )
        
        # Add output status
        beat_join_output = gr.Textbox(
            label="Output Status",
            show_copy_button=True,
            lines=10
        )

        # Create a partial function with vss bound to it
        process_fn = partial(process_beat_join, vss_instance=vss)
        
        # Handle button click
        beat_join_btn.click(
            fn=process_fn,
            inputs=[beat_join_folder, beat_join_audio],
            outputs=beat_join_output,
            show_progress="full"
        )
        
        # Add documentation
        gr.Markdown("""
        ### Beat-Synchronized Video Joining
        Join video clips and synchronize with background music.
        
        **Features:**
        - Audio synchronization
        - Automatic length adjustment
        - Progress tracking
        - Output size reporting
        
        **Process:**
        1. Clips are joined in sequence
        2. Audio is analyzed
        3. Final video is synchronized
        4. Output saved to beat-output folder
        
        **Notes:**
        - Clips should be in MP4 format
        - Audio should be MP3 or WAV
        - Output includes timestamp
        - Original timing is preserved
        """)
        
        # Add warning for large sets
        gr.Markdown("""
        ⚠️ **Warnings:**
        - Process may take longer than standard joining
        - Audio processing requires additional memory
        - Ensure adequate free disk space
        - Back up original files before processing
        """,
        visible=True
        )

if __name__ == "__main__":
    print("Beat Join Tab module loaded")