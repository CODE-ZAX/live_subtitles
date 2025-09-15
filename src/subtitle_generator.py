class SubtitleGenerator:
    def __init__(self):
        pass

    def generate_subtitles(self, segments, output_file, word_mode=True):
        with open(output_file, 'w', encoding='utf-8') as f:
            subtitle_index = 1
            word_count = 0
            
            if word_mode:
                # Word-by-word mode with highlighting
                word_buffer = []  # Buffer to keep track of last 3 words
                
                for segment in segments:
                    # Check if segment has word-level timestamps
                    if 'words' in segment and segment['words']:
                        # Generate rolling word subtitles with highlighting
                        for word_info in segment['words']:
                            word = word_info['word'].strip()
                            if word:  # Only process non-empty words
                                start_time = max(0, word_info['start'])
                                # Keep original word timing but ensure minimum duration
                                end_time = max(start_time + 0.5, word_info['end'])
                                
                                # Add current word to buffer
                                word_buffer.append({
                                    'word': word,
                                    'start': start_time,
                                    'end': end_time
                                })
                                
                                # Keep only last 3 words
                                if len(word_buffer) > 3:
                                    word_buffer.pop(0)
                                
                                # Create subtitle with last 3 words, highlighting current
                                subtitle_text = self.create_highlighted_subtitle(word_buffer)
                                
                                start_formatted = self.format_time(start_time)
                                end_formatted = self.format_time(end_time)
                                
                                f.write(f"{subtitle_index}\n")
                                f.write(f"{start_formatted} --> {end_formatted}\n")
                                f.write(f"{subtitle_text}\n\n")
                                subtitle_index += 1
                                word_count += 1
                    else:
                        # Fallback to segment-level subtitles if word timestamps not available
                        start_time = max(0, segment['start'])
                        end_time = max(start_time + 0.1, segment['end'])
                        
                        start_formatted = self.format_time(start_time)
                        end_formatted = self.format_time(end_time)
                        text = segment['text'].strip()
                        
                        if text:
                            f.write(f"{subtitle_index}\n")
                            f.write(f"{start_formatted} --> {end_formatted}\n")
                            f.write(f"{text}\n\n")
                            subtitle_index += 1
                            word_count += 1
            else:
                # Line-by-line mode (traditional subtitles)
                for segment in segments:
                    start_time = max(0, segment['start'])
                    end_time = max(start_time + 0.1, segment['end'])
                    
                    start_formatted = self.format_time(start_time)
                    end_formatted = self.format_time(end_time)
                    text = segment['text'].strip()
                    
                    if text:
                        f.write(f"{subtitle_index}\n")
                        f.write(f"{start_formatted} --> {end_formatted}\n")
                        f.write(f"{text}\n\n")
                        subtitle_index += 1
                        word_count += 1
            
            # Debug: Print word count
            print(f"Generated {word_count} subtitles in {output_file}")

    def create_highlighted_subtitle(self, word_buffer):
        """Create subtitle text with last 3 words, highlighting the current word"""
        if not word_buffer:
            return ""
        
        # Get the last word (currently spoken)
        current_word = word_buffer[-1]['word']
        
        # Create the display text with special markers for highlighting
        if len(word_buffer) == 1:
            # Only one word - highlight it
            return f"***{current_word}***"
        elif len(word_buffer) == 2:
            # Two words - highlight the second
            prev_word = word_buffer[0]['word']
            return f"{prev_word} ***{current_word}***"
        else:
            # Three words - highlight the last
            prev_words = [w['word'] for w in word_buffer[:-1]]
            return f"{' '.join(prev_words)} ***{current_word}***"

    def format_time(self, seconds):
        """Format seconds to SRT timestamp format (HH:MM:SS,mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milliseconds = int((seconds - int(seconds)) * 1000)
        return f"{hours:02}:{minutes:02}:{secs:02},{milliseconds:03}"