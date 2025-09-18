# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies including FFmpeg with all codecs
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libavcodec-extra \
    libavformat-dev \
    libavutil-dev \
    libswscale-dev \
    libswresample-dev \
    libavfilter-dev \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY server.py .
COPY Bangers-Regular.ttf .

# Copy the font file to src directory as well for easier access
COPY Bangers-Regular.ttf ./src/

# Create necessary directories
RUN mkdir -p uploads outputs frontend/build

# Create whisper cache directory
RUN mkdir -p /root/.cache/whisper

# Copy frontend build (will be built separately)
# Note: Frontend must be built before running docker-compose
COPY frontend/build/ ./frontend/build/

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app:/app/src
ENV PYTHONUNBUFFERED=1
ENV WHISPER_CACHE_DIR=/root/.cache/whisper

# Debug: List installed packages and check Python path
RUN pip list | grep -E "(fastapi|uvicorn|moviepy|whisper|srt)" || echo "Some packages might be missing"
RUN python -c "import sys; print('Python path:', sys.path)"

# Test basic imports
RUN python -c "import fastapi, uvicorn, moviepy, whisper, srt; print('All core packages imported successfully')"

# Run the server
CMD ["python", "server.py"]
