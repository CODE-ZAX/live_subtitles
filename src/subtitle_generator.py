class SubtitleGenerator:
    def __init__(self):
        pass

    def generate_subtitles(self, segments, output_file, word_mode=True):
        with open(output_file, 'w', encoding='utf-8') as f:
            subtitle_index = 1
            word_count = 0
            
            if word_mode:
                # Word-by-word mode - individual words only
                for segment in segments:
                    # Check if segment has word-level timestamps
                    if 'words' in segment and segment['words']:
                        # Generate individual word subtitles
                        for word_info in segment['words']:
                            word = word_info['word'].strip()
                            if word:  # Only process non-empty words
                                start_time = max(0, word_info['start'])
                                # Optimize timing for smooth captions
                                original_duration = word_info['end'] - start_time
                                
                                # For fast speech, use shorter durations
                                if original_duration < 0.3:
                                    end_time = start_time + max(0.2, original_duration)
                                else:
                                    end_time = word_info['end']
                                
                                start_formatted = self.format_time(start_time)
                                end_formatted = self.format_time(end_time)
                                
                                # Write individual word (no highlighting markers)
                                f.write(f"{subtitle_index}\n")
                                f.write(f"{start_formatted} --> {end_formatted}\n")
                                f.write(f"{word}\n\n")
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