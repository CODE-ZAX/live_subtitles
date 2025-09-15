from moviepy import VideoFileClip, TextClip, CompositeVideoClip
import srt

def extract_audio_from_video(video_path, audio_path):
    import moviepy as mp
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

def overlay_subtitles(video_path, srt_path, output_path, font_size=28, font='/Users/dev/Desktop/CODE/live-transcription-app/Bangers-Regular.ttf', color='white', bottom_padding=100, highlight_color='yellow'):
    """
    Overlay subtitles onto video with proper aspect ratio preservation
    """
    print("Loading video...")
    video = VideoFileClip(video_path)
    original_width, original_height = video.size
    print(f"Original video size: {original_width}x{original_height}")
    
    # Read SRT file
    print("Reading subtitles...")
    with open(srt_path, 'r', encoding='utf-8') as f:
        srt_content = f.read()
    
    subtitles = list(srt.parse(srt_content))
    print(f"Found {len(subtitles)} subtitles")
    
    # Create subtitle clips
    subtitle_clips = []
    
    for i, subtitle in enumerate(subtitles):
        if not subtitle.content.strip():
            continue
            
        print(f"Processing subtitle {i+1}/{len(subtitles)}: {subtitle.content[:30]}...")
        
        # Use exact timing from SRT subtitles - no adjustments
        start_time = subtitle.start.total_seconds()
        end_time = subtitle.end.total_seconds()
        duration = end_time - start_time
        
        # Clean text and handle highlighting
        text = subtitle.content.strip()
        
        # Check if this is word mode (has *** markers) or line mode
        is_word_mode = '***' in text
        
        if is_word_mode:
            # Word mode: Display last 3-4 words with current word highlighted
            clean_text = text.replace('***', '')
            text_color = highlight_color
        else:
            # Line mode: Display full line with proper wrapping
            clean_text = text
            text_color = color
        
        # Create text clip with proper sizing based on mode
        try:
            if is_word_mode:
                # Word mode: Simple display without wrapping
                txt_clip = TextClip(
                    text=clean_text,
                    font_size=font_size,
                    color=text_color,
                    bg_color="#000000CC",
                    margin=(10,10),
                    font=font,
                    method='label'
                ).with_position(('center', original_height - bottom_padding)).with_start(start_time).with_duration(duration)
            else:
                # Line mode: Enable text wrapping with screen width constraint
                max_width = int(original_width * 0.85)  # Use 85% of screen width
                txt_clip = TextClip(
                    text=clean_text,
                    font_size=font_size,
                    color=text_color,
                    font=font,
                    method='label',
                    size=(max_width, None)  # Enable wrapping
                ).with_position(('center', original_height - bottom_padding)).with_start(start_time).with_duration(duration)
            
            subtitle_clips.append(txt_clip)
            
        except Exception as e:
            print(f"Error creating text clip for subtitle {i+1}: {e} || {font}")
            continue
    
    print(f"Created {len(subtitle_clips)} subtitle clips")
    
    # Composite video
    print("Compositing video...")
    try:
        final_clips = [video] + subtitle_clips
        final_video = CompositeVideoClip(final_clips)
        
        # Write output
        print("Writing output video...")
        final_video.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            fps=video.fps,
        )
        
        print("Video processing complete!")
        
    except Exception as e:
        print(f"Error during video composition: {e}")
        raise
        
    finally:
        # Clean up
        try:
            video.close()
            if 'final_video' in locals():
                final_video.close()
            for clip in subtitle_clips:
                clip.close()
        except:
            pass

def create_text_clip_with_width(text, video, font_size, font, color, bottom_padding):
    """Create a text clip with proper width constraint for video"""
    max_width = int(video.w * 0.85)  # Use 85% of screen width
    
    return TextClip(
        text=text, 
        font_size=font_size, 
        font=font, 
        color=color, 
        method='label',
        size=(max_width, None)  # Enable text wrapping
    ).with_position(("center", video.h - bottom_padding))

def create_highlighted_text_clip(text, video, font_size, font, bottom_padding, font_color='white', highlight_color='yellow'):
    """Create a text clip with highlighting for word-by-word mode"""
    
    # Parse the text to create proper highlighting
    if '***' in text:
        # Split text and create highlighted version
        parts = text.split('***')
        if len(parts) == 3:  # word***word***word format
            before_highlight = parts[0].strip()
            highlighted_word = parts[1].strip()
            after_highlight = parts[2].strip()
            
            # Create the display text with proper spacing
            if before_highlight and after_highlight:
                display_text = f"{before_highlight} {highlighted_word} {after_highlight}"
            elif before_highlight:
                display_text = f"{before_highlight} {highlighted_word}"
            elif after_highlight:
                display_text = f"{highlighted_word} {after_highlight}"
            else:
                display_text = highlighted_word
        else:
            # Fallback: remove markers and use regular color
            display_text = text.replace('***', '')
    else:
        display_text = text
    
    # Word mode: Simple label display
    return TextClip(
        text=display_text,
        font_size=font_size,
        font=font,
        color=highlight_color if '***' in text else font_color,
        method='label'
    ).with_position(("center", video.h - bottom_padding))