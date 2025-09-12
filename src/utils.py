from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
import srt

def extract_audio_from_video(video_path, audio_path):
    import moviepy.editor as mp
    video = mp.VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path)

def save_transcription_to_file(transcription, file_path):
    with open(file_path, 'w') as f:
        f.write(transcription)

def generate_srt_subtitles(segments, output_path):
    with open(output_path, 'w') as f:
        for i, segment in enumerate(segments):
            start_time = format_time(segment['start'])
            end_time = format_time(segment['end'])
            text = segment['text'].strip()
            f.write(f"{i + 1}\n")
            f.write(f"{start_time} --> {end_time}\n")
            f.write(f"{text}\n\n")

def format_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02}:{minutes:02}:{seconds:02},000"

def overlay_subtitles(video_path, srt_path, output_path, font_size=20, font='Arial', color='white', bottom_padding=100):
    video = VideoFileClip(video_path)
    with open(srt_path, 'r') as f:
        srt_content = f.read()
    subtitles = list(srt.parse(srt_content))

    clips = [video]
    for sub in subtitles:
        txt_clip = (
            TextClip(sub.content, fontsize=font_size, font=font, color=color, bg_color='black', size=(video.w - 100, None), method='caption')
            .set_position(("center", video.h - bottom_padding))
            .set_start(sub.start.total_seconds())
            .set_duration((sub.end - sub.start).total_seconds())
        )
        clips.append(txt_clip)

    final = CompositeVideoClip(clips)
    final.write_videofile(output_path, codec='libx264', audio_codec='aac')