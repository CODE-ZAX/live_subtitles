import os
import tempfile
from moviepy.editor import VideoFileClip
import whisper

class Transcriber:
    def __init__(self, video_path):
        self.video_path = video_path
        self.transcribed_segments = []

    def transcribe_audio(self):
        # Extract audio from video
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
            audio_path = temp_audio.name
        video = VideoFileClip(self.video_path)
        video.audio.write_audiofile(audio_path, verbose=False, logger=None)

        # Load Whisper model and transcribe
        model = whisper.load_model("base")
        result = model.transcribe(audio_path, verbose=False)
        self.transcribed_segments = result['segments']

        # Clean up temp audio file
        os.remove(audio_path)

    def get_transcription(self):
        # Returns list of segments with text and timestamps
        return self.transcribed_segments