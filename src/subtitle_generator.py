class SubtitleGenerator:
    def __init__(self):
        pass

    def generate_subtitles(self, segments, output_file):
        with open(output_file, 'w') as f:
            for index, segment in enumerate(segments):
                start_time = self.format_time(segment['start'])
                end_time = self.format_time(segment['end'])
                text = segment['text'].strip()
                f.write(f"{index + 1}\n")
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{text}\n\n")

    def format_time(self, seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milliseconds = int((seconds - int(seconds)) * 1000)
        return f"{hours:02}:{minutes:02}:{secs:02},{milliseconds:03}"