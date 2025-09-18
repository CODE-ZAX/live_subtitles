import os
import sys
import argparse
from transcriber import Transcriber
from subtitle_generator import SubtitleGenerator
from utils import overlay_subtitles

def run_cli_mode(video_path, output_path="output_with_subtitles.mp4", srt_path="subtitles.srt"):
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
    subtitle_generator.generate_subtitles(transcription, srt_path)

    print("Step 3: Overlaying subtitles onto video...")
    # Overlay subtitles onto the video
    overlay_subtitles(video_path, srt_path, output_path)

    print(f"✓ Subtitles generated and saved to {srt_path}.")
    print(f"✓ Output video with subtitles saved as {output_path}.")
    print("Process completed successfully!")

def run_server_mode():
    """Run the FastAPI server"""
    import uvicorn
    from server import app
    print("Starting FastAPI server...")
    print("Server will be available at: http://localhost:8000")
    print("API documentation at: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)

def main():
    parser = argparse.ArgumentParser(description='AI Video Transcription - Generate subtitles for videos')
    parser.add_argument('--mode', choices=['server', 'cli'], default='server',
                       help='Choose between server mode (default) or CLI mode')
    parser.add_argument('--video', type=str,
                       help='Path to video file (required for CLI mode)')
    parser.add_argument('--output', type=str, default="output_with_subtitles.mp4",
                       help='Output video path (for CLI mode)')
    parser.add_argument('--srt', type=str, default="subtitles.srt",
                       help='Output SRT file path (for CLI mode)')
    
    args = parser.parse_args()
    
    if args.mode == 'server':
        print("Starting server mode...")
        run_server_mode()
    elif args.mode == 'cli':
        if not args.video:
            print("Error: --video argument is required for CLI mode")
            print("Usage: python main.py --mode cli --video <path_to_video>")
            sys.exit(1)
        run_cli_mode(args.video, args.output, args.srt)

if __name__ == "__main__":
    main()