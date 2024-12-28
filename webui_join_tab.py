import gradio as gr
import os
from pathlib import Path
import time

def process_join(input_folder, vss):
    """Process folder of clips for joining"""
    if not input_folder:
        return "No input folder specified."
    
    try:
        # Validate input folder
        valid, message = vss.validate_input_folder(input_folder)
        if not valid:
            return message

        # Initialize progress tracking
        update_progress = vss.get_progress_updater()
        start_time = time.time()
        
        # Resolve folder path
        input_folder = vss.resolve_folder_path(input_folder)
        
        status_messages = []
        status_messages.append(f"Processing folder: {input_folder}")
        
        # Count input files
        input_files = list(Path(input_folder).glob("*.mp4"))
        status_messages.append(f"Found {len(input_files)} clips to join")
        
        # Create VideoFileWriter redirect
        class ProgressRedirect:
            def __init__(self, messages_list):
                self.messages = messages_list
                
            def write(self, text):
                if "t:" in text:  # Writing progress
                    self.messages.append(f"Writing: {text.strip()}")
                elif "clip" in text.lower():  # Loading clip
                    self.messages.append(f"Loading: {text.strip()}")
                    
            def flush(self):
                pass

        # Redirect moviepy progress to our updater
        import sys
        original_stdout = sys.stdout
        sys.stdout = ProgressRedirect(status_messages)
        
        try:
            status_messages.append("\nStarting video join process...")
            vss.shuffle_joiner.join_videos(input_folder)
            
            # Get output file details
            output_dir = Path("output")
            output_files = list(output_dir.glob("joined_video_*.mp4"))
            if output_files:
                latest_output = max(output_files, key=lambda p: p.stat().st_mtime)
                size_mb = latest_output.stat().st_size / (1024 * 1024)
                
                processing_time = time.time() - start_time
                
                status_messages.append("\nJoin complete!")
                status_messages.append(f"Time taken: {processing_time:.1f} seconds")
                status_messages.append(f"Output file: {latest_output.name}")
                status_messages.append(f"File size: {size_mb:.1f} MB")
            else:
                status_messages.append("\nWarning: No output file found!")
                
        finally:
            # Restore stdout
            sys.stdout = original_stdout
            
        return "\n".join(status_messages)
            
    except Exception as e:
        return vss.process_error(e, "joining")

def create_join_tab(vss):
    """Create the join tab interface"""
    with gr.Column():
        # Input folder selection
        join_folder = gr.Textbox(
            label="Input Folder Path",
            info="Folder containing clips to join",
            placeholder="Enter path to folder containing clips"
        )
        
        # Add processing button
        join_btn = gr.Button(
            value="Join Clips",
            variant="primary"
        )
        
        # Add output status
        join_output = gr.Textbox(
            label="Output Status",
            show_copy_button=True,
            lines=10
        )
        
        # Handle button click
        join_btn.click(
            fn=lambda folder: process_join(folder, vss),
            inputs=[join_folder],
            outputs=join_output,
            show_progress="full"
        )
        
        # Add documentation
        gr.Markdown("""
        ### Video Joining
        Join a folder of video clips into a single output file.
        
        **Features:**
        - Automatic clip ordering
        - Progress tracking
        - Output size reporting
        - Processing time tracking
        
        **Notes:**
        - Clips should be in MP4 format
        - Clips should have matching dimensions
        - Output will be saved to the 'output' folder
        - Filename will include timestamp
        
        **Tips:**
        - Ensure all clips are properly encoded
        - Keep original files until output is verified
        - Check available disk space before joining large sets
        """)
        
        # Add warning for large sets
        gr.Markdown("""
        ⚠️ **Warning for Large Sets:**
        - Joining many clips requires significant memory
        - Long videos may take substantial processing time
        - Ensure adequate free disk space
        """,
        visible=True
        )

__all__ = ['create_join_tab']

if __name__ == "__main__":
    print("Join Tab module loaded")