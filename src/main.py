import os
import sys
from transcriber import Transcriber
from subtitle_generator import SubtitleGenerator
from utils import overlay_subtitles

def main(video_path):
    if not os.path.exists(video_path):
        print(f"Error: The file {video_path} does not exist.")
        sys.exit(1)

    # Transcribe audio from the video
    transcriber = Transcriber(video_path)
    transcriber.transcribe_audio()
    transcription = transcriber.get_transcription()

    # Generate subtitles (SRT file)
    subtitle_generator = SubtitleGenerator()
    srt_path = "subtitles.srt"
    subtitle_generator.generate_subtitles(transcription, srt_path)

    # Overlay subtitles onto the video
    output_video_path = "output_with_subtitles.mp4"
    overlay_subtitles(video_path, srt_path, output_video_path)

    print(f"Subtitles generated and saved to {srt_path}.")
    print(f"Output video with subtitles saved as {output_video_path}.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <path_to_video>")
        sys.exit(1)

    video_file_path = sys.argv[1]
    main(video_file_path)