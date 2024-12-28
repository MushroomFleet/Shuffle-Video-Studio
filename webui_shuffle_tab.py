import gradio as gr
import os
from pathlib import Path
import sys
import time
from webui_utils import InputSimulator

def process_shuffle(vss, input_folder, shuffle_type, reward_percentage=None, color_mode=None, 
                   transition_type=None, motion_mode=None, motion_speed=None, 
                   motion_min_score=None, motion_lookahead=None):
    """Process clips using selected shuffle mode"""
    if not input_folder:
        return "No input folder specified."
    
    try:
        # Validate input folder
        valid, message = vss.validate_input_folder(input_folder)
        if not valid:
            return message
        
        # Resolve folder path
        input_folder = vss.resolve_folder_path(input_folder)
        output_folder = vss.create_output_folder(f"shuffled")
        
        update_progress = vss.get_progress_updater()
        status = []  # Create a list to store status messages
        
        def update_status(msg):
            status.append(msg)
            return "\n".join(status)
        
        update_status(f"Processing folder: {input_folder}")
        update_status(f"Output folder: {output_folder}")
        
        # Process according to shuffle type
        if shuffle_type == "simple":
            update_status("Using simple shuffle mode...")
            vss.shuffle_splits.simple_shuffle(input_folder, output_folder)
            
        elif shuffle_type == "size_reward" and reward_percentage is not None:
            update_status(f"Using size-reward shuffle mode ({reward_percentage}% reward)...")
            original_stdin = sys.stdin
            try:
                simulated_input = InputSimulator([float(reward_percentage)])
                sys.stdin = simulated_input
                vss.shuffle_splits.size_reward_shuffle(input_folder, output_folder)
            finally:
                sys.stdin = original_stdin
                
        elif shuffle_type == "color" and color_mode is not None:
            if color_mode == "similarity":
                update_status("Using color similarity shuffle mode...")
                vss.color_shuffle.color_based_shuffle(input_folder, output_folder, mode="similarity")
            elif color_mode == "transition" and transition_type is not None:
                update_status(f"Using color transition shuffle mode ({transition_type})...")
                vss.color_shuffle.color_based_shuffle(input_folder, output_folder, 
                                                    mode="transition", 
                                                    transition_type=transition_type)
            else:
                return "Invalid color mode or missing transition type."
                
        elif shuffle_type == "motion":
            from motion_vector_extractor import MotionVectorExtractor
            from motion_manifest_manager import MotionManifest
            from motion_sequence_sorter import MotionSequenceSorter, SortingConfig
            
            update_status("\nInitializing motion analysis...")
            update_status(f"Analysis speed: {motion_speed}")
            update_status(f"Minimum transition score: {motion_min_score}")
            update_status(f"Transition lookahead: {motion_lookahead}")
            
            # Initialize motion vector extractor
            extractor = MotionVectorExtractor(speed_mode=motion_speed or "balanced")
            
            # Create manifest
            manifest_path = Path(output_folder) / "motion_manifest.json"
            manifest = MotionManifest(manifest_path)
            
            # Analyze all clips in the folder
            clip_paths = [f for f in Path(input_folder).glob("*.mp4")]
            total_clips = len(clip_paths)
            
            update_status(f"\nFound {total_clips} clips to analyze")
            start_time = time.time()
            
            for idx, clip_path in enumerate(clip_paths, 1):
                try:
                    update_status(f"\nAnalyzing clip {idx}/{total_clips}: {clip_path.name}")
                    motion_data = extractor.analyze_clip(str(clip_path))
                    manifest.add_clip(motion_data)
                    
                    # Add detailed motion info
                    start_motion = motion_data.start_motion.primary_direction.value
                    end_motion = motion_data.end_motion.primary_direction.value
                    update_status(f"✓ Motion detected: {start_motion} → {end_motion}")
                    
                except Exception as e:
                    update_status(f"⚠ Error analyzing {clip_path.name}: {str(e)}")
            
            analysis_time = time.time() - start_time
            update_status(f"\nMotion analysis complete! Time taken: {analysis_time:.1f} seconds")
            
            # Analyze transitions
            update_status("\nAnalyzing potential transitions...")
            manifest.analyze_all_transitions()
            manifest.save()
            
            # Configure sorting
            config = SortingConfig(
                min_transition_score=float(motion_min_score or 0.5),
                transition_lookahead=int(motion_lookahead or 3)
            )
            
            # Sort clips
            update_status("\nSorting clips based on motion analysis...")
            sorter = MotionSequenceSorter(manifest, config)
            sequence = sorter.sort_clips_natural_eye()
            
            # Generate report
            report = sorter.get_transition_report()
            report_path = Path(output_folder) / "transition_report.txt"
            
            update_status("\nGenerating transition report...")
            with open(report_path, 'w') as f:
                f.write("Motion Transition Report\n")
                f.write("======================\n\n")
                transition_count = 0
                for t in report:
                    f.write(f"From: {Path(t['from_clip']).name}\n")
                    f.write(f"To: {Path(t['to_clip']).name}\n")
                    f.write(f"Score: {t['score']:.2f}\n")
                    f.write(f"Notes: {t['notes']}\n\n")
                    transition_count += 1
            
            # Apply sequence to files
            update_status("\nCopying sorted clips to output folder...")
            sorter.apply_sequence_to_files(Path(output_folder))
            
            # Final statistics
            total_time = time.time() - start_time
            stats = manifest.get_statistics()
            update_status(f"\nProcessing complete!")
            update_status(f"Total clips processed: {stats['total_clips']}")
            update_status(f"Total transitions analyzed: {stats['total_transitions']}")
            update_status(f"Average transition score: {stats['avg_transition_score']:.2f}")
            update_status(f"Total time taken: {total_time:.1f} seconds")
            update_status(f"\nOutput saved to: {output_folder}")
            update_status(f"Transition report saved to: {report_path}")
            
        else:
            return "Invalid shuffle configuration."
            
        update_status(f"\nShuffle complete. Output in: {output_folder}")
        return "\n".join(status)  # Return all status messages as a single string
        
    except Exception as e:
        if 'original_stdin' in locals():
            sys.stdin = original_stdin
        return vss.process_error(e, "shuffling")

def create_shuffle_tab(vss):
    """Create the shuffle tab interface"""
    with gr.Column():
        shuffle_folder = gr.Textbox(
            label="Input Folder Path",
            info="Folder containing clips to shuffle"
        )
        
        shuffle_type = gr.Radio(
            choices=["simple", "size_reward", "color", "motion"],
            label="Shuffle Type",
            value="simple"
        )
        
        # Size reward controls
        with gr.Group() as size_group:
            reward_percentage = gr.Slider(
                minimum=1,
                maximum=100,
                value=50,
                label="Reward Percentage",
                info="Percentage of largest files to keep",
                visible=False
            )
        
        # Color controls
        with gr.Group() as color_group:
            color_mode = gr.Radio(
                choices=["similarity", "transition"],
                label="Color Mode",
                value="similarity",
                visible=False
            )
            
            transition_type = gr.Radio(
                choices=["rainbow", "sunset", "ocean"],
                label="Transition Type",
                value="rainbow",
                visible=False
            )
        
        # Motion controls
        with gr.Group() as motion_group:
            motion_mode = gr.Radio(
                choices=["natural_eye"],
                label="Motion Analysis Mode",
                value="natural_eye",
                info="Natural Eye mode guides viewer attention through the scene",
                visible=False
            )
            
            motion_speed = gr.Radio(
                choices=["fast", "balanced", "precise"],
                label="Analysis Speed",
                value="balanced",
                info="Affects analysis detail and processing time",
                visible=False
            )
            
            motion_min_score = gr.Slider(
                minimum=0.0,
                maximum=1.0,
                value=0.5,
                step=0.1,
                label="Minimum Transition Score",
                info="Higher values require more precise motion matches",
                visible=False
            )
            
            motion_lookahead = gr.Slider(
                minimum=1,
                maximum=5,
                value=3,
                step=1,
                label="Transition Lookahead",
                info="Number of clips to analyze ahead for better sequences",
                visible=False
            )
    
    def update_shuffle_visibility(shuffle_type):
        """Update visibility of mode-specific controls"""
        return [
            gr.update(visible=shuffle_type == "size_reward"),  # reward_percentage
            gr.update(visible=shuffle_type == "color"),        # color_mode
            gr.update(visible=shuffle_type == "color" and color_mode == "transition"),  # transition_type
            gr.update(visible=shuffle_type == "motion"),  # motion_mode
            gr.update(visible=shuffle_type == "motion"),  # motion_speed
            gr.update(visible=shuffle_type == "motion"),  # motion_min_score
            gr.update(visible=shuffle_type == "motion"),  # motion_lookahead
        ]
    
    def update_color_visibility(color_mode):
        """Update visibility of color-specific controls"""
        return gr.update(visible=color_mode == "transition")
    
    # Connect visibility update events
    shuffle_type.change(
        fn=update_shuffle_visibility,
        inputs=[shuffle_type],
        outputs=[reward_percentage, color_mode, transition_type,
                motion_mode, motion_speed, motion_min_score, motion_lookahead]
    )
    
    color_mode.change(
        fn=update_color_visibility,
        inputs=[color_mode],
        outputs=transition_type
    )
    
    # Add processing button
    shuffle_btn = gr.Button(
        value="Shuffle Clips",
        variant="primary"
    )
    
    # Add output status
    shuffle_output = gr.Textbox(
        label="Output Status",
        show_copy_button=True,
        lines=15
    )
    
    # Handle button click with lambda wrapper
    shuffle_btn.click(
        fn=lambda folder, type, reward, color, trans, mode, speed, score, look: process_shuffle(
            vss, folder, type, reward, color, trans, mode, speed, score, look
        ),
        inputs=[
            shuffle_folder,
            shuffle_type,
            reward_percentage,
            color_mode,
            transition_type,
            motion_mode,
            motion_speed,
            motion_min_score,
            motion_lookahead
        ],
        outputs=shuffle_output,
        show_progress="full"
    )
    
    # Add documentation
    gr.Markdown("""
    ### Shuffle Modes
    
    **Simple Shuffle**
    - Basic random ordering
    - Fast processing
    - Suitable for quick tests
    
    **Size Reward Shuffle**
    - Keeps larger files (usually higher quality)
    - Adjustable reward percentage
    - Good for quality-based selection
    
    **Color Shuffle**
    - Similarity: Groups similar colors
    - Transitions: Creates color flow effects
    - Options for rainbow, sunset, ocean transitions
    
    **Motion Shuffle (New!)**
    - Analyzes clip motion patterns
    - Creates visually flowing sequences
    - Guides viewer attention naturally
    - Speed vs. precision options
    - Detailed transition reporting
    """)