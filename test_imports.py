#!/usr/bin/env python3
"""
Test script to verify all imports work correctly
"""

import sys
import os

print("Python version:", sys.version)
print("Python path:", sys.path)
print("Current working directory:", os.getcwd())
print("Files in current directory:", os.listdir('.'))

print("\nTesting imports...")

try:
    import fastapi
    print("✓ FastAPI imported successfully")
except ImportError as e:
    print("✗ FastAPI import failed:", e)

try:
    import uvicorn
    print("✓ Uvicorn imported successfully")
except ImportError as e:
    print("✗ Uvicorn import failed:", e)

try:
    import moviepy
    print("✓ MoviePy imported successfully")
except ImportError as e:
    print("✗ MoviePy import failed:", e)

try:
    import whisper
    print("✓ Whisper imported successfully")
except ImportError as e:
    print("✗ Whisper import failed:", e)

try:
    import srt
    print("✓ SRT imported successfully")
except ImportError as e:
    print("✗ SRT import failed:", e)

# Test local imports
print("\nTesting local imports...")

try:
    from transcriber import Transcriber
    print("✓ Transcriber imported successfully")
except ImportError as e:
    print("✗ Transcriber import failed:", e)

try:
    from subtitle_generator import SubtitleGenerator
    print("✓ SubtitleGenerator imported successfully")
except ImportError as e:
    print("✗ SubtitleGenerator import failed:", e)

try:
    from utils import overlay_subtitles
    print("✓ Utils imported successfully")
except ImportError as e:
    print("✗ Utils import failed:", e)

print("\nImport test completed!")
