import gradio as gr
import os
from pathlib import Path
import time

def process_beat_split(vss, video_file, audio_file, bars_per_segment):
    """Process video with beat-synchronized splitting"""
    if not video_file or not audio_file:
        return "Both video and audio files are required."
    
    try:
        update_progress = vss.get_progress_updater()
        all_messages = []
        
        # Create permanent copies of uploaded files
        video_path = vss.create_permanent_file(video_file, "input_video")
        audio_path = vss.create_permanent_file(audio_file, "input_audio")
        
        all_messages.append(update_progress(f"Processing video: {os.path.basename(video_path)}"))
        all_messages.append(update_progress(f"Using audio: {os.path.basename(audio_path)}"))
        
        # Create output folder
        video_name = os.path.splitext(os.path.basename(video_path))[0]
        output_folder = vss.create_output_folder(f"beat_split_{video_name}")
        all_messages.append(update_progress(f"Output folder: {output_folder}"))
        
        # Override output folder for beat splitter
        original_get_output_folder = vss.beat_splitter.get_output_folder
        def patched_get_output_folder(input_file):
            return output_folder
        vss.beat_splitter.get_output_folder = patched_get_output_folder
        
        try:
            # Initialize beat detection
            all_messages.append(update_progress("Starting beat analysis..."))
            all_messages.append(update_progress(f"Using {bars_per_segment} bars per segment"))
            
            # Process video with beat synchronization
            start_time = time.time()
            vss.beat_splitter.split_video_on_bars(video_path, audio_path, int(bars_per_segment))
            processing_time = time.time() - start_time
            
            # Count output files and report results
            output_files = list(Path(output_folder).glob("*.mp4"))
            
            all_messages.append(update_progress("\nProcessing complete!"))
            all_messages.append(update_progress(f"Time taken: {processing_time:.1f} seconds"))
            all_messages.append(update_progress(f"Generated {len(output_files)} beat-synchronized clips"))
            all_messages.append(update_progress(f"Output saved to: {output_folder}"))
            
        finally:
            # Restore original function
            vss.beat_splitter.get_output_folder = original_get_output_folder
            
            # Clean up temporary files
            vss.clean_temp_files(video_path, audio_path)
            
        return "\n".join(all_messages)
            
    except Exception as e:
        return vss.process_error(e, "beat-synchronized splitting")

def create_beat_tab(vss):
    """Create the beat-synchronized split tab interface"""
    with gr.Row():
        beat_video = gr.File(
            label="Input Video",
            file_types=[".mp4"],
            file_count="single"
        )
        beat_audio = gr.File(
            label="Input Audio",
            file_types=[".mp3", ".wav"],
            file_count="single"
        )
        bars_per_segment = gr.Number(
            label="Bars per Segment",
            value=1,
            minimum=1,
            maximum=8,
            step=1,
            info="Number of musical bars per clip"
        )
    
    # Add info text about bars
    gr.Markdown("""
    **Bars per Segment Guide:**
    - 1 bar: Short, rhythmic cuts (≈4 beats)
    - 2 bars: Standard musical phrase
    - 4 bars: Full musical sequence
    - 8 bars: Extended musical section
    """)
    
    # Add processing button
    beat_split_btn = gr.Button(
        value="Split on Beats",
        variant="primary"
    )
    
    # Add output status
    beat_split_output = gr.Textbox(
        label="Output Status",
        show_copy_button=True,
        lines=10
    )
    
    # Handle button click with lambda wrapper
    beat_split_btn.click(
        fn=lambda video, audio, bars: process_beat_split(vss, video, audio, bars),
        inputs=[
            beat_video,
            beat_audio,
            bars_per_segment
        ],
        outputs=beat_split_output,
        show_progress="full"
    )
    
    # Add technical documentation
    gr.Markdown("""
    ### Beat-Synchronized Video Splitting
    Split video based on musical beats detected in the audio file. 
    The video will be split into segments aligned with the musical structure.
    
    **Features:**
    - Automatic beat detection
    - Musical bar synchronization
    - CUDA-accelerated processing
    - Progress tracking
    
    **Tips:**
    - Use high-quality audio for better beat detection
    - Choose bars per segment based on music structure
    - Lower values create more dynamic cuts
    - Higher values maintain longer sequences
    """)