#!/usr/bin/env python3

import os
import sys
from datetime import datetime
import yt_dlp
from moviepy.editor import VideoFileClip
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from urllib.parse import urlparse, parse_qs
import inquirer
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_KEY = os.getenv('YOUTUBE_API_KEY')

class YouTubeDownloader:
    def __init__(self, api_key):
        self.youtube = build('youtube', 'v3', developerKey=api_key)

    def get_video_details(self, video_id):
        """Get video details using YouTube Data API."""
        try:
            response = self.youtube.videos().list(
                part="snippet,contentDetails,statistics,status",
                id=video_id
            ).execute()

            if not response['items']:
                raise ValueError('Video not found or is private')

            video = response['items'][0]
            return {
                'title': video['snippet']['title'],
                'channel': video['snippet']['channelTitle'],
                'view_count': video['statistics']['viewCount'],
                'definition': video['contentDetails']['definition'],
                'privacy_status': video['status']['privacyStatus']
            }
        except HttpError as e:
            if e.resp.status == 403:
                raise Exception("API Key error: Please check your YouTube Data API key")
            raise Exception(f"YouTube API error: {str(e)}")

    def validate_video(self, video_id):
        """Validate video availability."""
        try:
            details = self.get_video_details(video_id)
            if details['privacy_status'] != 'public':
                raise ValueError(f"Video is {details['privacy_status']}, not accessible")
            return details
        except Exception as e:
            raise Exception(f"Video validation failed: {str(e)}")

def extract_video_id(url):
    """Extract video ID from YouTube URL."""
    query = urlparse(url)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch':
            return parse_qs(query.query)['v'][0]
        if query.path[:7] == '/embed/':
            return query.path.split('/')[2]
        if query.path[:3] == '/v/':
            return query.path.split('/')[2]
    raise ValueError('Invalid YouTube URL')

def time_to_seconds(time_str):
    """Convert time string (HH:MM:SS) to seconds."""
    try:
        time_obj = datetime.strptime(time_str, '%H:%M:%S')
        return time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second
    except ValueError:
        print("Invalid time format. Please use HH:MM:SS")
        sys.exit(1)

def download_video(url, start_time, end_time, output_format):
    """Download and process YouTube video segment."""
    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    try:
        # Initialize YouTube API client and validate video
        yt = YouTubeDownloader(API_KEY)
        video_id = extract_video_id(url)
        video_info = yt.validate_video(video_id)
        
        print("\nVideo Information:")
        print(f"Title: {video_info['title']}")
        print(f"Channel: {video_info['channel']}")
        print(f"Views: {video_info['view_count']}")
        print(f"Quality: {video_info['definition'].upper()}")
        
        # Configure download options
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': 'downloads/temp_%(title)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'geo_bypass': True,
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
            'prefer_ffmpeg': True
        }

        # Download video
        print("\nDownloading video...")
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_path = ydl.prepare_filename(info)
                if not video_path.endswith('.mp4'):
                    video_path = video_path.rsplit('.', 1)[0] + '.mp4'
        except Exception as e:
            print(f"\nError during download: {str(e)}")
            print("\nRetrying with different options...")
            ydl_opts['format'] = 'bestaudio[ext=m4a]+bestvideo[ext=mp4]/best'
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_path = ydl.prepare_filename(info)
                if not video_path.endswith('.mp4'):
                    video_path = video_path.rsplit('.', 1)[0] + '.mp4'

        # Process video segment
        print("Processing video segment...")
        video = VideoFileClip(video_path)
        
        # Validate time inputs
        start_seconds = time_to_seconds(start_time)
        end_seconds = time_to_seconds(end_time)
        if start_seconds >= end_seconds:
            raise ValueError("End time must be after start time")
        if end_seconds > video.duration:
            raise ValueError(f"End time exceeds video duration of {int(video.duration)} seconds")

        # Extract and save segment
        clip = video.subclip(start_seconds, end_seconds)
        title = info.get('title', 'video').replace('/', '-')
        output_filename = f'downloads/clip_{title[:40]}.{output_format.lower()}'
        
        print("Saving video...")
        if output_format.upper() == 'MP4':
            clip.write_videofile(output_filename, 
                               codec='libx264',
                               audio_codec='aac',
                               temp_audiofile='temp-audio.m4a',
                               remove_temp=True)
        else:
            clip.audio.write_audiofile(output_filename)
            
        # Clean up
        video.close()
        clip.close()
        
        # Cleanup all temporary files
        download_dir = 'downloads'
        video_title = info.get('title', '').replace('/', '-')
        for file in os.listdir(download_dir):
            if 'temp_' in file:  # Match any file with 'temp_' in the name
                temp_file_path = os.path.join(download_dir, file)
                try:
                    os.remove(temp_file_path)
                    print(f"Cleaned up temporary file: {file}")
                except Exception as e:
                    print(f"Warning: Could not remove temporary file {file}: {e}")
            
        print(f"\nDone! Your clip has been saved to: {output_filename}")

    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        if isinstance(e, HttpError):
            print("\nYouTube API error. Please check your API key and quota limits")
        sys.exit(1)

def main():
    """Main function to handle user input."""
    questions = [
        inquirer.Text('url', message="Enter the YouTube URL"),
        inquirer.List('format',
                     message="Choose output format",
                     choices=['MP4', 'MP3']),
        inquirer.Text('start_time', message="Enter start time (HH:MM:SS)"),
        inquirer.Text('end_time', message="Enter end time (HH:MM:SS)")
    ]
    
    answers = inquirer.prompt(questions)
    print("\nProcessing your request...")
    download_video(answers['url'], answers['start_time'], 
                  answers['end_time'], answers['format'])

if __name__ == "__main__":
    if not API_KEY:
        print("YouTube API key not found!")
        print("Please create a .env file with your YouTube Data API key.")
        print("You can copy .env.example to .env and add your API key.")
        print("Get an API key from: https://console.cloud.google.com/apis/credentials")
        sys.exit(1)
    main()
