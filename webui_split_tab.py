import gradio as gr
import os
from pathlib import Path

def process_standard_split(vss, video_file, duration):
    """Process video file using standard splitting"""
    if not video_file:
        return "No video file provided."
    
    try:
        # Create permanent copy of uploaded file
        video_path = vss.create_permanent_file(video_file, "input_video")
        progress_text = [f"Processing video: {video_path}"]
        
        # Create output folder based on video name
        video_name = os.path.splitext(os.path.basename(video_path))[0]
        output_folder = vss.create_output_folder(f"split_{video_name}")
        
        # Override output folder for video splitter
        original_get_output_folder = vss.video_splitter.get_output_folder
        def patched_get_output_folder(input_file):
            return output_folder
        vss.video_splitter.get_output_folder = patched_get_output_folder
        
        try:
            # Process video
            update_progress = vss.get_progress_updater()
            progress_text.append(f"Starting video split with {duration} second segments...")
            progress_text.append(f"Output folder: {output_folder}")
            
            # Run the splitter
            vss.video_splitter.split_video_cuda(video_path, int(duration))
            
            # Count output files
            output_files = list(Path(output_folder).glob("*.mp4"))
            progress_text.append(f"Split complete! Generated {len(output_files)} clips")
            progress_text.append(f"Output saved to: {output_folder}")
            
        finally:
            # Restore original function
            vss.video_splitter.get_output_folder = original_get_output_folder
            
            # Clean up temporary files
            vss.clean_temp_files(video_path)
            
        return "\n".join(progress_text)
            
    except Exception as e:
        return vss.process_error(e, "video splitting")

def create_split_tab(vss):
    """Create the standard split tab interface"""
    with gr.Row():
        split_video = gr.File(
            label="Input Video",
            file_types=[".mp4"],
            file_count="single"
        )
        split_duration = gr.Number(
            label="Clip Duration (seconds)",
            value=2,
            minimum=1,
            maximum=60,
            step=1
        )
    
    # Add processing button
    split_btn = gr.Button(
        value="Split Video",
        variant="primary"
    )
    
    # Add output status
    split_output = gr.Textbox(
        label="Output Status",
        show_copy_button=True,
        lines=10
    )
    
    # Handle button click with lambda wrapper
    split_btn.click(
        fn=lambda video, duration: process_standard_split(vss, video, duration),
        inputs=[
            split_video,
            split_duration
        ],
        outputs=split_output,
        show_progress="full"
    )
    
    # Add interface documentation
    gr.Markdown("""
    ### Standard Video Splitting
    Upload a video file and specify the desired clip duration. The video will be split into segments of equal length.
    
    **Features:**
    - CUDA-accelerated processing when available
    - Automatic file organization
    - Progress tracking
    - Clean temporary file handling
    """)