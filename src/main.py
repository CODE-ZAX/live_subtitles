import os
import sys
import argparse
from transcriber import Transcriber
from subtitle_generator import SubtitleGenerator
from utils import overlay_subtitles
from gui import ModernTranscriptionApp
import tkinter as tk

def run_cli_mode(video_path):
    """Run the transcription in command-line mode"""
    if not os.path.exists(video_path):
        print(f"Error: The file {video_path} does not exist.")
        sys.exit(1)

    print("Starting transcription process...")
    print("Step 1: Transcribing audio...")
    
    # Transcribe audio from the video
    transcriber = Transcriber(video_path)
    transcriber.transcribe_audio()
    transcription = transcriber.get_transcription()
    
    print("Step 2: Generating subtitles...")
    # Generate subtitles (SRT file)
    subtitle_generator = SubtitleGenerator()
    srt_path = "subtitles.srt"
    subtitle_generator.generate_subtitles(transcription, srt_path)

    print("Step 3: Overlaying subtitles onto video...")
    # Overlay subtitles onto the video
    output_video_path = "output_with_subtitles.mp4"
    overlay_subtitles(video_path, srt_path, output_video_path)

    print(f"✓ Subtitles generated and saved to {srt_path}.")
    print(f"✓ Output video with subtitles saved as {output_video_path}.")
    print("Process completed successfully!")

def run_gui_mode():
    """Run the transcription in GUI mode"""
    import customtkinter as ctk
    root = ctk.CTk()
    app = ModernTranscriptionApp(root)
    root.mainloop()

def main():
    parser = argparse.ArgumentParser(description='Live Transcription App - Generate subtitles for videos')
    parser.add_argument('--mode', choices=['gui', 'cli'], default='gui',
                       help='Choose between GUI mode (default) or CLI mode')
    parser.add_argument('--video', type=str,
                       help='Path to video file (required for CLI mode)')
    
    args = parser.parse_args()
    
    if args.mode == 'gui':
        print("Starting GUI mode...")
        run_gui_mode()
    elif args.mode == 'cli':
        if not args.video:
            print("Error: --video argument is required for CLI mode")
            print("Usage: python main.py --mode cli --video <path_to_video>")
            sys.exit(1)
        run_cli_mode(args.video)

if __name__ == "__main__":
    main()