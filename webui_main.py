import gradio as gr
from webui_studio import VideoShuffleStudio
from webui_split_tab import create_split_tab
from webui_beat_tab import create_beat_tab
from webui_shuffle_tab import create_shuffle_tab
from webui_join_tab import create_join_tab
from webui_beat_join_tab import create_beat_join_tab

def create_ui():
    """Create and configure the main UI interface"""
    vss = VideoShuffleStudio()
    
    with gr.Blocks(title="Video Shuffle Studio") as app:
        gr.Markdown("# Video Shuffle Studio")
        gr.Markdown(vss.check_cuda())
        
        with gr.Tabs():
            # Create tabs and pass VSS instance through the interface components
            with gr.Tab("Standard Split"):
                create_split_tab(vss)

            with gr.Tab("Beat Split"):
                create_beat_tab(vss)

            with gr.Tab("Shuffle"):
                create_shuffle_tab(vss)

            with gr.Tab("Join"):
                create_join_tab(vss)

            with gr.Tab("Beat Join"):
                create_beat_join_tab(vss)

        return app

if __name__ == "__main__":
    # Import success messages
    print("Loading Video Shuffle Studio modules...")
    print("- Studio core loaded")
    print("- Split module loaded")
    print("- Beat processing loaded")
    print("- Shuffle module loaded")
    print("- Join module loaded")
    print("- Beat join module loaded")
    
    # Create and launch the UI
    app = create_ui()
    app.launch(
        server_name="127.0.0.1",  # Local only
        server_port=7860,
        share=False  # Disable public URL
    )