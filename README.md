# ClipCutter

A Python tool to download and extract segments from YouTube videos with high-quality audio and video support. Perfect for creating clips from longer videos while maintaining original quality.

## Features
- Download specific segments from YouTube videos
- High-quality MP4 video output with audio
- MP3 audio-only extraction option
- Automatic format selection for best quality
- Smart error handling and retries
- Automatic cleanup of temporary files
- YouTube Data API integration for video validation
- Progress tracking during download and processing

## Requirements
- Python 3.8+
- FFmpeg (for video processing)
- YouTube Data API key

## Setup

### 1. Get YouTube Data API Key
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the YouTube Data API v3 for your project
4. Go to Credentials and create an API key
5. Copy the API key

### 2. Install FFmpeg
FFmpeg is required for video processing. Install it using your package manager:

macOS (using Homebrew):
```bash
brew install ffmpeg
```

Linux:
```bash
sudo apt-get install ffmpeg  # Ubuntu/Debian
sudo yum install ffmpeg      # CentOS/RHEL
```

Windows:
Download from [FFmpeg website](https://ffmpeg.org/download.html)

### 3. Configure Environment
1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
2. Edit `.env` and add your YouTube API key:
   ```
   YOUTUBE_API_KEY=your_api_key_here
   ```

## Installation

### Option 1: Local Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/clipcutter.git
cd clipcutter

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Option 2: Docker Installation
If you prefer using Docker:

```bash
# Build the Docker image
docker build -t clipcutter .

# Run the container
docker run -it \
  -v "$(pwd)/downloads:/app/downloads" \
  -v "$(pwd)/.env:/app/.env:ro" \
  clipcutter
```

The `-v` flags create volume mounts that:
- Share the downloads directory between your computer and the container
- Make your .env file available to the container (read-only)

## Usage
```bash
python clipcutter.py
```

The interactive prompt will guide you through:
1. Enter the YouTube URL
2. Choose output format (MP4/MP3)
3. Enter start time (HH:MM:SS format)
4. Enter end time (HH:MM:SS format)

The tool will then:
1. Validate the video and retrieve information
2. Download the video in best available quality
3. Extract the specified segment
4. Save the final clip in the `downloads` directory
5. Automatically clean up temporary files

### Example
```bash
$ python clipcutter.py
? Enter the YouTube URL: https://www.youtube.com/watch?v=...
? Choose output format: MP4
? Enter start time (HH:MM:SS): 00:01:30
? Enter end time (HH:MM:SS): 00:02:45

Video Information:
Title: Example Video
Channel: Example Channel
Views: 1000000
Quality: HD

Downloading video...
Processing video segment...
Saving video...

Done! Your clip has been saved to: downloads/clip_Example_Video.mp4
```

## Troubleshooting
- If download fails, the tool automatically retries with alternative format options
- Ensure your YouTube API key has sufficient quota
- Check that FFmpeg is properly installed and accessible
- For region-restricted videos, use a VPN or different region

## License
MIT License
