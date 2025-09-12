# Live Transcription App

This project provides a live transcription service that takes a video file as input and generates a new video file with subtitles based on the transcribed audio.

## Project Structure

```
live-transcription-app
├── src
│   ├── main.py
│   ├── transcriber.py
│   ├── subtitle_generator.py
│   └── utils.py
├── requirements.txt
└── README.md
```

## Installation

To set up the project, clone the repository and install the required dependencies. You can do this by running:

```bash
pip install -r requirements.txt
```

## Usage

1. Place your video file in the appropriate directory.
2. Run the main application:

```bash
python src/main.py path/to/your/video.mp4
```

3. The output video with subtitles will be generated in the same directory.

## Components

- **main.py**: The entry point of the application that handles video input and output.
- **transcriber.py**: Contains the `Transcriber` class for audio extraction and transcription.
- **subtitle_generator.py**: Contains the `SubtitleGenerator` class for creating subtitle files.
- **utils.py**: Utility functions for file handling and audio extraction.

## Contributing

Feel free to submit issues or pull requests if you have suggestions or improvements for the project.

## License

This project is licensed under the MIT License.