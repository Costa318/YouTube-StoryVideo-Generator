#!/usr/bin/env python3
"""
Phase 0: YouTube Transcript Analysis
Extracts transcripts from successful horror channels for story pattern analysis.
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class YouTubeTranscriptAnalyzer:
    """Analyzes YouTube horror channels by extracting transcripts and metadata."""
    
    def __init__(self, output_dir: str = "research"):
        self.output_dir = Path(output_dir)
        self.transcripts_dir = self.output_dir / "transcripts"
        self.metadata_dir = self.output_dir / "metadata"
        
        # Create directories if they don't exist
        self.transcripts_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
    
    def check_dependencies(self) -> bool:
        """Check if yt-dlp is installed."""
        try:
            result = subprocess.run(['yt-dlp', '--version'], 
                                  capture_output=True, text=True, check=True)
            logger.info(f"yt-dlp version: {result.stdout.strip()}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("yt-dlp not found. Install with: pip install yt-dlp")
            return False
    
    def load_channels_config(self, config_path: str) -> List[Dict]:
        """Load channel configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            return config.get('channels', [])
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {config_path}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON config: {e}")
            return []
    
    def extract_channel_videos(self, channel_url: str, min_views: int = 100000, 
                             max_videos: int = 20) -> List[Dict]:
        """Extract video information from a YouTube channel."""
        logger.info(f"Extracting videos from channel: {channel_url}")
        
        # Ensure channel URL has /videos suffix for yt-dlp
        if not channel_url.endswith('/videos'):
            channel_url = channel_url.rstrip('/') + '/videos'
        
        # yt-dlp command to get video information
        cmd = [
            'yt-dlp',
            '--flat-playlist',
            '--print', '%(id)s|%(title)s|%(view_count)s|%(duration)s|%(upload_date)s',
            '--playlist-end', str(max_videos),
            channel_url
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            videos = []
            
            for line in result.stdout.strip().split('\n'):
                if '|' in line:
                    parts = line.split('|')
                    if len(parts) >= 4:
                        # The format is: ID|title (possibly with |)|views|duration|date
                        # We need to find the last 3 parts (views, duration, date) and reconstruct title
                        video_id = parts[0]
                        
                        # Last parts are: views, duration, upload_date
                        view_count = parts[-3] if len(parts) >= 3 else 'NA'
                        duration = parts[-2] if len(parts) >= 2 else 'NA'
                        upload_date = parts[-1] if len(parts) >= 1 else 'NA'
                        
                        # Title is everything between ID and the last 3 parts
                        title_parts = parts[1:-3] if len(parts) > 4 else parts[1:-2] if len(parts) == 4 else [parts[1]]
                        title = '|'.join(title_parts).strip()
                        
                        # Filter by view count
                        try:
                            views = int(view_count) if view_count != 'NA' else 0
                            if views >= min_views:
                                videos.append({
                                    'id': video_id,
                                    'title': title,
                                    'view_count': views,
                                    'duration': duration,
                                    'upload_date': upload_date,
                                    'url': f'https://www.youtube.com/watch?v={video_id}'
                                })
                        except (ValueError, TypeError):
                            logger.warning(f"Could not parse video data: {line}")
                            continue
            
            logger.info(f"Found {len(videos)} videos with >= {min_views} views")
            return videos
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error extracting videos: {e}")
            return []
    
    def extract_transcript(self, video_url: str, video_id: str) -> Optional[Tuple[str, Dict]]:
        """Extract transcript and metadata from a single video."""
        logger.info(f"Extracting transcript for video: {video_id}")
        
        # Check for transcript files with different language suffixes
        possible_files = [
            self.transcripts_dir / f"{video_id}.en-orig.vtt",
            self.transcripts_dir / f"{video_id}.en.vtt", 
            self.transcripts_dir / f"{video_id}.vtt"
        ]
        
        transcript_file = None
        for file_path in possible_files:
            if file_path.exists():
                transcript_file = file_path
                break
        
        metadata_file = self.metadata_dir / f"{video_id}.json"
        
        # Skip if already exists
        if transcript_file and metadata_file.exists():
            logger.info(f"Transcript already exists for {video_id}, skipping")
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            return str(transcript_file), metadata
        
        # Extract transcript (use en-orig for original English captions)
        transcript_cmd = [
            'yt-dlp',
            '--write-auto-subs',
            '--sub-langs', 'en-orig,en',  # Try en-orig first, fallback to en
            '--sub-format', 'vtt',
            '--skip-download',
            '--output', str(self.transcripts_dir / f"{video_id}.%(ext)s"),
            video_url
        ]
        
        # Extract metadata using JSON format to avoid parsing issues
        metadata_cmd = [
            'yt-dlp',
            '--dump-json',
            '--skip-download',
            video_url
        ]
        
        try:
            # Get transcript
            subprocess.run(transcript_cmd, capture_output=True, check=True)
            
            # Get metadata as JSON
            result = subprocess.run(metadata_cmd, capture_output=True, text=True, check=True)
            
            if result.stdout.strip():
                video_info = json.loads(result.stdout.strip())
                metadata = {
                    'id': video_info.get('id', video_id),
                    'title': video_info.get('title', ''),
                    'view_count': video_info.get('view_count', 0) or 0,
                    'like_count': video_info.get('like_count', 0) or 0,
                    'duration': str(video_info.get('duration', '')),
                    'upload_date': video_info.get('upload_date', ''),
                    'description': (video_info.get('description', '') or '')[:1000],  # Truncate long descriptions
                    'url': video_url,
                    'transcript_file': str(transcript_file)
                }
                
                # Save metadata  
                with open(metadata_file, 'w') as f:
                    json.dump(metadata, f, indent=2)
                
                # Find the actual transcript file that was created
                for file_path in possible_files:
                    if file_path.exists():
                        return str(file_path), metadata
            
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to extract transcript for {video_id}: {e}")
            return None
        
        return None
    
    def clean_transcript(self, vtt_file: str) -> str:
        """Clean VTT transcript file to plain text."""
        try:
            with open(vtt_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Simple VTT cleaning - extract just the text lines
            lines = content.split('\n')
            text_lines = []
            
            for line in lines:
                line = line.strip()
                # Skip VTT headers, timestamps, and empty lines
                if (line and 
                    not line.startswith('WEBVTT') and
                    not line.startswith('NOTE') and
                    '-->' not in line and
                    not line.isdigit()):
                    # Remove HTML tags and duplicate text
                    clean_line = line.replace('<c>', '').replace('</c>', '')
                    if clean_line and clean_line not in text_lines[-3:]:  # Avoid duplicates
                        text_lines.append(clean_line)
            
            return ' '.join(text_lines)
            
        except Exception as e:
            logger.error(f"Error cleaning transcript {vtt_file}: {e}")
            return ""
    
    def analyze_channels(self, config_path: str, min_views: int = 100000, 
                        max_videos_per_channel: int = 20) -> Dict:
        """Main method to analyze horror channels."""
        if not self.check_dependencies():
            return {}
        
        channels = self.load_channels_config(config_path)
        if not channels:
            return {}
        
        analysis_results = {
            'channels_analyzed': len(channels),
            'total_videos': 0,
            'successful_transcripts': 0,
            'channels': {}
        }
        
        for channel in channels:
            channel_name = channel.get('name', 'unknown')
            channel_url = channel.get('url', '')
            
            if not channel_url:
                logger.warning(f"No URL provided for channel: {channel_name}")
                continue
            
            logger.info(f"Analyzing channel: {channel_name}")
            
            # Get videos from channel
            videos = self.extract_channel_videos(
                channel_url, min_views, max_videos_per_channel
            )
            
            channel_results = {
                'name': channel_name,
                'url': channel_url,
                'videos_found': len(videos),
                'transcripts_extracted': 0,
                'videos': []
            }
            
            # Extract transcripts for each video
            for video in videos:
                result = self.extract_transcript(video['url'], video['id'])
                if result:
                    transcript_file, metadata = result
                    clean_text = self.clean_transcript(transcript_file)
                    
                    video_data = {
                        **video,
                        'metadata': metadata,
                        'transcript_length': len(clean_text),
                        'transcript_file': transcript_file
                    }
                    
                    channel_results['videos'].append(video_data)
                    channel_results['transcripts_extracted'] += 1
                    analysis_results['successful_transcripts'] += 1
            
            analysis_results['channels'][channel_name] = channel_results
            analysis_results['total_videos'] += len(videos)
        
        # Save analysis summary
        summary_file = self.output_dir / 'analysis_summary.json'
        with open(summary_file, 'w') as f:
            json.dump(analysis_results, f, indent=2)
        
        logger.info(f"Analysis complete. Results saved to {summary_file}")
        return analysis_results


def main():
    parser = argparse.ArgumentParser(description='YouTube Horror Channel Transcript Analyzer')
    parser.add_argument('--channels', required=True, 
                       help='Path to channels configuration JSON file')
    parser.add_argument('--extract-transcripts', action='store_true',
                       help='Extract transcripts from videos')
    parser.add_argument('--min-views', type=int, default=100000,
                       help='Minimum view count for videos (default: 100000)')
    parser.add_argument('--max-videos', type=int, default=20,
                       help='Maximum videos per channel (default: 20)')
    parser.add_argument('--output', default='research',
                       help='Output directory (default: research)')
    
    args = parser.parse_args()
    
    if args.extract_transcripts:
        analyzer = YouTubeTranscriptAnalyzer(args.output)
        results = analyzer.analyze_channels(
            args.channels, 
            args.min_views,
            args.max_videos
        )
        
        print(f"\nAnalysis Summary:")
        print(f"Channels analyzed: {results.get('channels_analyzed', 0)}")
        print(f"Total videos found: {results.get('total_videos', 0)}")
        print(f"Successful transcripts: {results.get('successful_transcripts', 0)}")
    else:
        print("Use --extract-transcripts to start analysis")


if __name__ == '__main__':
    main()