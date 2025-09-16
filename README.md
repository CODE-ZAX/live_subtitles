# 🎬 AI Video Transcription Studio

> **Professional AI-powered video transcription with beautiful subtitle overlays**

Transform your videos with state-of-the-art AI speech recognition and create stunning subtitle overlays with smooth rolling captions - just like professional TV broadcasts!

## ✨ Features

🤖 **AI-Powered Transcription**

- OpenAI Whisper integration for accurate speech recognition
- Support for multiple languages and accents
- Word-level timing precision

🎨 **Beautiful Subtitle Overlays**

- Customizable fonts, sizes, and colors
- Smooth rolling word-by-word captions
- Professional TV-style subtitle animations
- Auto-clearing on speech pauses

🖥️ **Cross-Platform**

- Windows, macOS, and Linux support
- Modern GUI with dark/light themes
- Command-line interface for automation

🎥 **Video Processing**

- Preserves original video quality and aspect ratio
- Supports MP4, AVI, MOV, and more formats
- Batch processing capabilities

## 🚀 Quick Start

### Automatic Installation

**Windows:**

```cmd
# Download and double-click:
install_windows.bat
```

**macOS:**

```bash
# Download and run:
chmod +x install_mac.sh && ./install_mac.sh
```

**Linux:**

```bash
# Download and run:
python3 setup.py
```

### Manual Installation

1. **Prerequisites:**

   - Python 3.8+
   - FFmpeg (auto-installed by setup)

2. **Install:**

   ```bash
   git clone <repository-url>
   cd ai-video-transcription-studio
   python setup.py
   ```

3. **Run:**
   ```bash
   python src/main.py
   ```

## 🎯 Usage

### GUI Mode (Recommended)

1. Launch the application
2. Click "Browse" to select your video
3. Customize subtitle options:
   - Font family and size
   - Colors and positioning
   - Word-by-word or line-by-line mode
4. Click "Start Transcription"
5. Wait for AI processing
6. Get your subtitled video!

### CLI Mode

```bash
# Basic usage
python src/main.py --mode cli --video my_video.mp4

# With custom options
python src/main.py --mode cli --video my_video.mp4 \
  --font-size 32 --color yellow --highlight-color white
```

## 🎨 Customization

### Subtitle Styling

- **Fonts**: System fonts or custom TTF files
- **Colors**: Any hex color or CSS color name
- **Positioning**: Adjustable bottom padding
- **Animation**: Word-by-word rolling or traditional line display

### Advanced Options

- **Window Size**: Control how many words show at once
- **Timing**: Automatic pause detection and array clearing
- **Quality**: High-quality video encoding with aspect ratio preservation

## 📁 Project Structure

```
ai-video-transcription-studio/
├── src/
│   ├── main.py              # Main application entry
│   ├── gui.py               # Modern GUI interface
│   ├── transcriber.py       # AI transcription engine
│   ├── subtitle_generator.py # SRT subtitle creation
│   └── utils.py             # Video processing utilities
├── setup.py                 # Universal installer
├── install_windows.bat      # Windows installer
├── install_mac.sh           # macOS installer
├── build_distribution.py    # Build script for releases
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🛠️ Development

### Building Distribution

```bash
python build_distribution.py
```

### Running Tests

```bash
# Test with sample video
python src/main.py --mode cli --video sample.mp4
```

## 🆘 Troubleshooting

### Common Issues

**FFmpeg not found:**

```bash
# Windows (with chocolatey)
choco install ffmpeg

# macOS (with homebrew)
brew install ffmpeg

# Linux (Ubuntu/Debian)
sudo apt install ffmpeg
```

**Python version issues:**

- Ensure Python 3.8+ is installed
- On macOS, use `python3` instead of `python`
- On Windows, reinstall Python with "Add to PATH" checked

**Memory issues:**

- Close other applications during processing
- Use shorter video clips for testing
- Ensure 4GB+ RAM available

### Performance Tips

- Use MP4 format for best compatibility
- Keep videos under 30 minutes for optimal processing
- Close unnecessary applications during transcription

## 🤝 Contributing

We welcome contributions! Please feel free to:

- Report bugs and issues
- Suggest new features
- Submit pull requests
- Improve documentation

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI Whisper for AI transcription
- MoviePy for video processing
- CustomTkinter for modern GUI
- The open-source community for inspiration

---

**Made with ❤️ for content creators worldwide**

_Transform your videos • Engage your audience • Create professional content_
