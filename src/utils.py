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

def create_dynamic_text_function(word_events):
    """Create a function that returns text based on time"""
    def text_at_time(t):
        word_window = []
        
        # Find all words that should be visible at time t
        for event in word_events:
            if event['start'] <= t:
                word_window.append(event['word'])
                # Keep only last 4 words
                if len(word_window) > 4:
                    word_window.pop(0)
            else:
                break
        
        return ' '.join(word_window) if word_window else ""
    
    return text_at_time

def create_rolling_word_clips(word_subtitles, video, font_size, font, color, highlight_color, bottom_padding, original_width, original_height):
    """
    Create a single dynamic text clip with no overlaps
    """
    print("Creating live rolling word clip...")
    
    # Parse all individual words with their timing
    word_events = []
    for subtitle in word_subtitles:
        start_time = subtitle.start.total_seconds()
        end_time = subtitle.end.total_seconds()
        
        # Each subtitle contains just one word
        word = subtitle.content.strip()
        if word:
            word_events.append({
                'start': start_time,
                'end': end_time,
                'word': word
            })
    
    if not word_events:
        return []
    
    # Sort by start time
    word_events.sort(key=lambda x: x['start'])
    
    # Create non-overlapping sequential clips
    clips = []
    word_window = []
    last_word_end = 0
    
    for i, event in enumerate(word_events):
        print(f"Processing word {i+1}/{len(word_events)}: {event['word']}")
        
        # Check if there's a pause > 1 second since last word
        if last_word_end > 0 and (event['start'] - last_word_end) > 1.0:
            print(f"  Gap detected: {event['start'] - last_word_end:.2f}s - clearing window")
            word_window = []  # Clear the rolling window
        
        # Add new word to rolling window
        word_window.append(event['word'])
        
        # Remove oldest word if window exceeds 4 words
        if len(word_window) > 4:
            word_window.pop(0)
        
        # Update last word end time for gap detection
        last_word_end = event['end']
        
        # Create display text from current window
        display_text = ' '.join(word_window)
        
        # Calculate precise timing to avoid overlap
        start_time = event['start']
        
        # End exactly when the next word starts, or at the end of this word
        if i < len(word_events) - 1:
            next_start = word_events[i + 1]['start']
            end_time = min(next_start, event['end'])
        else:
            end_time = event['end']
        
        duration = max(0.1, end_time - start_time)  # Ensure minimum duration
        
        try:
            # Create clip that ends before next one starts
            txt_clip = TextClip(
                text=display_text,
                font_size=font_size,
                color=color,
                bg_color="#000000CC",
                margin=(10,10),
                font=font,
                method='label'
            ).with_position(('center', original_height - bottom_padding)).with_start(start_time).with_duration(duration)
            
            clips.append(txt_clip)
            
        except Exception as e:
            print(f"Error creating word clip: {e}")
            continue
    
    print(f"Created {len(clips)} sequential non-overlapping clips")
    return clips

def overlay_subtitles(video_path, srt_path, output_path, font_size=28, font='/Users/dev/Desktop/CODE/live-transcription-app/Bangers-Regular.ttf', color='white', bottom_padding=100, highlight_color='yellow'):
    """
    Overlay subtitles onto video with rolling word window system
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
    
    # In word mode, all subtitles are individual words
    # In line mode, subtitles are complete sentences
    # For now, assume all subtitles are word mode (individual words)
    word_mode_subtitles = []
    line_mode_subtitles = []
    
    for subtitle in subtitles:
        if not subtitle.content.strip():
            continue
        
        # Check if it's a single word (word mode) or multiple words (line mode)
        words_in_subtitle = subtitle.content.strip().split()
        if len(words_in_subtitle) == 1:
            word_mode_subtitles.append(subtitle)
        else:
            line_mode_subtitles.append(subtitle)
    
    print(f"Word mode: {len(word_mode_subtitles)}, Line mode: {len(line_mode_subtitles)}")
    
    # Create subtitle clips
    subtitle_clips = []
    
    # Handle word mode with rolling window
    if word_mode_subtitles:
        word_clips = create_rolling_word_clips(
            word_mode_subtitles, 
            video, 
            font_size, 
            font, 
            color, 
            color,  # Use same color for word mode
            bottom_padding, 
            original_width, 
            original_height
        )
        subtitle_clips.extend(word_clips)
    
    # Handle line mode normally
    for subtitle in line_mode_subtitles:
        try:
            start_time = subtitle.start.total_seconds()
            end_time = subtitle.end.total_seconds()
            duration = end_time - start_time
            
            max_width = int(original_width * 0.85)
            txt_clip = TextClip(
                text=subtitle.content.strip(),
                font_size=font_size,
                color=color,
                font=font,
                method='label',
                size=(max_width, None)
            ).with_position(('center', original_height - bottom_padding)).with_start(start_time).with_duration(duration)
            
            subtitle_clips.append(txt_clip)
            
        except Exception as e:
            print(f"Error creating line mode clip: {e}")
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