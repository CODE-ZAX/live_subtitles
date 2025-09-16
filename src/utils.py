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
    Create smooth live caption style rolling word clips
    """
    print("Creating smooth live caption clips...")
    
    # Parse all individual words with their timing
    word_events = []
    for subtitle in word_subtitles:
        start_time = subtitle.start.total_seconds()
        end_time = subtitle.end.total_seconds()
        
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
    
    # Create smooth caption segments
    clips = []
    word_window = []
    last_word_end = 0
    
    # Group words into smooth segments to reduce clip count
    i = 0
    while i < len(word_events):
        segment_start = word_events[i]['start']
        segment_words = []
        segment_timings = []
        
        # Collect words for this segment (until gap > 1s or significant timing change)
        j = i
        while j < len(word_events):
            event = word_events[j]
            
            # Check for pause > 1 second
            if last_word_end > 0 and (event['start'] - last_word_end) > 1.0:
                print(f"  Gap detected: {event['start'] - last_word_end:.2f}s - starting new segment")
                word_window = []  # Clear window on gap
            
            # Add word to current segment
            word_window.append(event['word'])
            if len(word_window) > 4:
                word_window.pop(0)
            
            segment_words.append(' '.join(word_window))
            segment_timings.append(event['start'])
            last_word_end = event['end']
            
            # Break segment if:
            # 1. Next word has > 0.5s gap (for smoother transitions)
            # 2. We've collected enough words for smooth playback
            # 3. We've reached the end of words
            if (j + 1 < len(word_events) and 
                word_events[j + 1]['start'] - event['end'] > 0.5) or \
               (j - i + 1) >= 8:  # Max 8 words per segment
                break
                
            j += 1
        
        # Create smooth segment with multiple state changes
        if segment_words:
            # Ensure j is within bounds
            if j >= len(word_events):
                j = len(word_events) - 1
            
            segment_end = word_events[j]['end']
            total_duration = segment_end - segment_start
            
            # Create individual clips for each word state in this segment
            for k, (display_text, word_start) in enumerate(zip(segment_words, segment_timings)):
                try:
                    # Calculate duration for this word state
                    if k < len(segment_timings) - 1:
                        word_duration = segment_timings[k + 1] - word_start
                    else:
                        word_duration = segment_end - word_start
                    
                    # Ensure minimum duration for readability
                    word_duration = max(0.15, word_duration)
                    
                    # Skip if duration is invalid
                    if word_duration <= 0:
                        continue
                    
                    txt_clip = TextClip(
                        text=display_text,
                        font_size=font_size,
                        color=color,
                        bg_color="#000000CC",
                        margin=(8,8),  # Smaller margin for smoother look
                        font=font,
                        method='label'
                    ).with_position(('center', original_height - bottom_padding)).with_start(word_start).with_duration(word_duration)
                    
                    clips.append(txt_clip)
                    print(f"  Word state: '{display_text}' at {word_start:.2f}s for {word_duration:.2f}s")
                    
                except Exception as e:
                    print(f"Error creating word state clip: {e}")
                    continue
        
        i = j + 1
    
    print(f"Created {len(clips)} smooth caption clips")
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