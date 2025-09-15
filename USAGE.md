# Live Transcription App Usage Guide

## Overview

This app generates subtitles for videos using AI transcription and overlays them with precise timing synchronization.

## Usage Modes

### GUI Mode (Default)

Launch the graphical user interface:

```bash
python src/main.py
# or
python src/main.py --mode gui
```

### CLI Mode

Process a video file from command line:

```bash
python src/main.py --mode cli --video path/to/your/video.mp4
```

## Features

### Subtitle Synchronization

- Uses Whisper AI for accurate speech recognition
- Precise timestamp matching with speaker speech
- Automatic subtitle timing validation
- Enhanced visibility with stroke and background

### Output

- Generates `subtitles.srt` file with timestamped text
- Creates `output_with_subtitles.mp4` with overlaid subtitles
- High-quality video output with proper audio sync

## Requirements

- Python 3.7+
- Required packages listed in `requirements.txt`
- Video files in MP4 format (recommended)

## Example

```bash
# Process a video file
python src/main.py --mode cli --video my_video.mp4

# Output:
# Starting transcription process...
# Step 1: Transcribing audio...
# Step 2: Generating subtitles...
# Step 3: Overlaying subtitles onto video...
# ✓ Subtitles generated and saved to subtitles.srt.
# ✓ Output video with subtitles saved as output_with_subtitles.mp4.
# Process completed successfully!
```
