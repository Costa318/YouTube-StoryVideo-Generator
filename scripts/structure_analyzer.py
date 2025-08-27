#!/usr/bin/env python3
"""
Phase 0B: Content Structure Analysis
Analyzes transcript structure to identify story boundaries, transitions, and engagement patterns.
"""

import json
import re
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ContentStructureAnalyzer:
    """Analyzes horror video content structure from transcripts."""
    
    def __init__(self, research_dir: str = "research"):
        self.research_dir = Path(research_dir)
        self.transcripts_dir = self.research_dir / "transcripts"
        self.metadata_dir = self.research_dir / "metadata"
        self.output_dir = self.research_dir / "structure_analysis"
        
        # Create output directory
        self.output_dir.mkdir(exist_ok=True)
        
        # Load analysis summary for video metadata
        self.video_data = self._load_video_metadata()
        
        # Story boundary markers (common patterns in horror transcripts)
        self.story_markers = [
            # Numbered story markers
            r'story\s+(?:number\s+)?(\d+)',
            r'(?:tale|story)\s+(\d+)',
            r'(\d+)(?:st|nd|rd|th)?\s+story',
            
            # Chapter/section markers  
            r'chapter\s+(\d+)',
            r'part\s+(\d+)',
            r'section\s+(\d+)',
            
            # Submission/source markers
            r'submitted\s+by',
            r'sent\s+in\s+by',
            r'this\s+story\s+(?:was\s+)?sent',
            r'(?:story|tale)\s+from',
            
            # Title/introduction patterns
            r'titled\s+["\']([^"\']+)["\']',
            r'called\s+["\']([^"\']+)["\']',
            r'the\s+story\s+is\s+called',
            
            # Transition phrases
            r'(?:now|next)\s+(?:story|tale)',
            r'(?:moving|going)\s+on\s+to',
            r'let[\']?s\s+(?:move|go)\s+(?:on\s+)?to',
            r'here[\']?s\s+(?:another|the\s+next)',
        ]
        
        # Compiled regex patterns
        self.story_pattern = re.compile('|'.join(self.story_markers), re.IGNORECASE)
        
    def _load_video_metadata(self) -> Dict:
        """Load video metadata from analysis summary."""
        try:
            summary_file = self.research_dir / 'analysis_summary.json'
            with open(summary_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning("Analysis summary not found")
            return {}
    
    def clean_vtt_transcript(self, vtt_file: str) -> str:
        """Clean VTT transcript file to plain text with timestamps."""
        try:
            with open(vtt_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            text_segments = []
            current_time = None
            
            for line in lines:
                line = line.strip()
                
                # Skip VTT headers and empty lines
                if (not line or 
                    line.startswith('WEBVTT') or
                    line.startswith('NOTE') or
                    line.isdigit()):
                    continue
                
                # Extract timestamp
                if '-->' in line:
                    # Format: 00:00:15.120 --> 00:00:18.040
                    start_time = line.split(' --> ')[0]
                    current_time = self._parse_timestamp(start_time)
                    continue
                
                # Clean text content
                if line and current_time is not None:
                    # Remove HTML tags and clean text
                    clean_line = re.sub(r'<[^>]+>', '', line)
                    clean_line = clean_line.strip()
                    
                    if clean_line:
                        text_segments.append({
                            'timestamp_seconds': current_time,
                            'text': clean_line
                        })
            
            return text_segments
            
        except Exception as e:
            logger.error(f"Error cleaning transcript {vtt_file}: {e}")
            return []
    
    def _parse_timestamp(self, timestamp_str: str) -> int:
        """Parse VTT timestamp to seconds."""
        try:
            # Format: 00:00:15.120
            time_parts = timestamp_str.split(':')
            hours = int(time_parts[0])
            minutes = int(time_parts[1])
            seconds = float(time_parts[2])
            
            return int(hours * 3600 + minutes * 60 + seconds)
        except:
            return 0
    
    def identify_story_boundaries(self, text_segments: List[Dict]) -> List[Dict]:
        """Identify story boundaries within transcript segments."""
        stories = []
        current_story = None
        story_count = 0
        
        for i, segment in enumerate(text_segments):
            text = segment['text'].lower()
            
            # Check for story boundary markers
            if self.story_pattern.search(text):
                # End current story if exists
                if current_story:
                    current_story['end_time'] = segment['timestamp_seconds']
                    current_story['end_index'] = i - 1
                    stories.append(current_story)
                
                # Start new story
                story_count += 1
                current_story = {
                    'story_number': story_count,
                    'start_time': segment['timestamp_seconds'],
                    'start_index': i,
                    'boundary_text': segment['text'][:100] + '...',
                    'segments': []
                }
            
            # Add segment to current story
            if current_story:
                current_story['segments'].append(segment)
        
        # Close final story
        if current_story:
            current_story['end_time'] = text_segments[-1]['timestamp_seconds'] if text_segments else 0
            current_story['end_index'] = len(text_segments) - 1
            stories.append(current_story)
        
        return stories
    
    def analyze_video_structure(self, video_id: str, channel_name: str) -> Dict:
        """Analyze the structure of a single video."""
        logger.info(f"Analyzing structure for video: {video_id}")
        
        # Find transcript file
        transcript_file = None
        for suffix in ['.en-orig.vtt', '.en.vtt', '.vtt']:
            potential_file = self.transcripts_dir / f"{video_id}{suffix}"
            if potential_file.exists():
                transcript_file = potential_file
                break
        
        if not transcript_file:
            logger.warning(f"No transcript found for {video_id}")
            return {}
        
        # Get video metadata
        video_metadata = self._get_video_metadata(video_id, channel_name)
        
        # Clean transcript
        text_segments = self.clean_vtt_transcript(transcript_file)
        if not text_segments:
            return {}
        
        # Identify stories
        stories = self.identify_story_boundaries(text_segments)
        
        # Calculate story statistics
        total_duration = text_segments[-1]['timestamp_seconds'] if text_segments else 0
        
        story_stats = []
        for story in stories:
            duration = story['end_time'] - story['start_time']
            word_count = sum(len(seg['text'].split()) for seg in story['segments'])
            
            story_stats.append({
                'story_number': story['story_number'],
                'start_time_formatted': self._seconds_to_timestamp(story['start_time']),
                'duration_seconds': duration,
                'duration_minutes': round(duration / 60, 1),
                'word_count': word_count,
                'boundary_text': story['boundary_text']
            })
        
        analysis = {
            'video_id': video_id,
            'channel': channel_name,
            'metadata': video_metadata,
            'total_duration_seconds': total_duration,
            'total_duration_minutes': round(total_duration / 60, 1),
            'story_count': len(stories),
            'stories': story_stats,
            'average_story_duration': round(total_duration / len(stories) / 60, 1) if stories else 0,
            'transcript_segments': len(text_segments)
        }
        
        return analysis
    
    def _get_video_metadata(self, video_id: str, channel_name: str) -> Dict:
        """Get video metadata from analysis summary."""
        try:
            channel_data = self.video_data.get('channels', {}).get(channel_name, {})
            videos = channel_data.get('videos', [])
            
            for video in videos:
                if video.get('id') == video_id:
                    return {
                        'title': video.get('title', ''),
                        'view_count': video.get('view_count', 0),
                        'duration': video.get('duration', ''),
                        'url': video.get('url', '')
                    }
        except:
            pass
        
        return {}
    
    def _seconds_to_timestamp(self, seconds: int) -> str:
        """Convert seconds to HH:MM:SS format."""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def analyze_channel(self, channel_name: str, max_videos: int = 5) -> Dict:
        """Analyze structure for all videos from a channel."""
        logger.info(f"Analyzing channel structure: {channel_name}")
        
        channel_data = self.video_data.get('channels', {}).get(channel_name, {})
        videos = channel_data.get('videos', [])
        
        if not videos:
            logger.warning(f"No videos found for channel: {channel_name}")
            return {}
        
        # Limit analysis to recent videos
        videos_to_analyze = videos[:max_videos]
        
        channel_analysis = {
            'channel_name': channel_name,
            'videos_analyzed': len(videos_to_analyze),
            'videos': [],
            'summary': {}
        }
        
        all_story_counts = []
        all_durations = []
        all_avg_story_lengths = []
        
        for video in videos_to_analyze:
            video_id = video.get('id')
            if video_id:
                analysis = self.analyze_video_structure(video_id, channel_name)
                if analysis:
                    channel_analysis['videos'].append(analysis)
                    
                    # Collect stats for summary
                    all_story_counts.append(analysis['story_count'])
                    all_durations.append(analysis['total_duration_minutes'])
                    if analysis['average_story_duration'] > 0:
                        all_avg_story_lengths.append(analysis['average_story_duration'])
        
        # Calculate channel summary statistics
        if channel_analysis['videos']:
            channel_analysis['summary'] = {
                'avg_stories_per_video': round(sum(all_story_counts) / len(all_story_counts), 1),
                'avg_video_duration_minutes': round(sum(all_durations) / len(all_durations), 1),
                'avg_story_duration_minutes': round(sum(all_avg_story_lengths) / len(all_avg_story_lengths), 1) if all_avg_story_lengths else 0,
                'total_stories_analyzed': sum(all_story_counts),
                'story_count_range': f"{min(all_story_counts)}-{max(all_story_counts)}" if all_story_counts else "0"
            }
        
        return channel_analysis
    
    def run_structure_analysis(self, target_channels: List[str] = None) -> Dict:
        """Run complete structure analysis for specified channels."""
        if not target_channels:
            target_channels = ['Let\'s Read Podcast', 'Mr. Nightmare']
        
        results = {
            'analysis_date': '2025-08-27',
            'channels_analyzed': len(target_channels),
            'channels': {}
        }
        
        for channel in target_channels:
            channel_analysis = self.analyze_channel(channel, max_videos=5)
            if channel_analysis:
                results['channels'][channel] = channel_analysis
        
        # Save results
        output_file = self.output_dir / 'content_structure_analysis.json'
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Structure analysis complete. Results saved to {output_file}")
        return results


def main():
    analyzer = ContentStructureAnalyzer()
    
    # Analyze key channels for structure patterns
    target_channels = ['Let\'s Read Podcast', 'Mr. Nightmare']
    
    results = analyzer.run_structure_analysis(target_channels)
    
    # Print summary
    print("\n📊 CONTENT STRUCTURE ANALYSIS SUMMARY")
    print("=" * 50)
    
    for channel_name, channel_data in results['channels'].items():
        summary = channel_data.get('summary', {})
        print(f"\n🎯 {channel_name}:")
        print(f"   Videos Analyzed: {channel_data['videos_analyzed']}")
        print(f"   Avg Stories per Video: {summary.get('avg_stories_per_video', 'N/A')}")
        print(f"   Avg Video Duration: {summary.get('avg_video_duration_minutes', 'N/A')} minutes")
        print(f"   Avg Story Length: {summary.get('avg_story_duration_minutes', 'N/A')} minutes")
        print(f"   Story Count Range: {summary.get('story_count_range', 'N/A')}")


if __name__ == '__main__':
    main()