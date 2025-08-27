#!/usr/bin/env python3
"""
Fabric AI integration for horror story pattern analysis.
Analyzes transcripts to extract story hooks, pacing, and horror elements.
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FabricAnalyzer:
    """Uses Fabric AI to analyze horror story transcripts for patterns."""
    
    def __init__(self, input_dir: str = "research/transcripts", 
                 output_dir: str = "research/fabric_analysis"):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Fabric patterns for horror story analysis
        self.patterns = {
            'extract_story_hooks': 'extract_story_hooks',
            'analyze_pacing_structure': 'analyze_pacing_structure',
            'extract_horror_elements': 'extract_horror_elements'
        }
    
    def check_fabric_available(self) -> bool:
        """Check if Fabric is available and configured."""
        try:
            result = subprocess.run(['fabric', '--help'], 
                                  capture_output=True, text=True, check=True)
            logger.info("Fabric is available")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("Fabric not found. Install and configure Fabric first.")
            return False
    
    def clean_transcript_text(self, vtt_file: Path) -> str:
        """Extract clean text from VTT transcript file."""
        try:
            with open(vtt_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Clean VTT format to plain text
            lines = content.split('\n')
            text_lines = []
            
            for line in lines:
                line = line.strip()
                # Skip VTT headers, timestamps, and metadata
                if (line and 
                    not line.startswith('WEBVTT') and
                    not line.startswith('NOTE') and
                    '-->' not in line and
                    not line.isdigit() and
                    not line.startswith('<')):
                    
                    # Remove HTML-like tags
                    clean_line = line.replace('<c>', '').replace('</c>', '')
                    clean_line = clean_line.replace('<c.colorE5E5E5>', '').replace('</c>', '')
                    
                    if clean_line and len(clean_line) > 2:
                        text_lines.append(clean_line)
            
            # Join and clean up
            full_text = ' '.join(text_lines)
            # Remove excessive whitespace
            full_text = ' '.join(full_text.split())
            
            return full_text
            
        except Exception as e:
            logger.error(f"Error cleaning transcript {vtt_file}: {e}")
            return ""
    
    def analyze_with_fabric(self, text: str, pattern: str) -> Optional[str]:
        """Analyze text using a specific Fabric pattern."""
        try:
            # Run fabric with the specified pattern
            cmd = ['fabric', '--pattern', pattern]
            
            result = subprocess.run(
                cmd,
                input=text,
                text=True,
                capture_output=True,
                check=True,
                timeout=120  # 2 minute timeout
            )
            
            return result.stdout.strip()
            
        except subprocess.TimeoutExpired:
            logger.warning(f"Fabric analysis timed out for pattern {pattern}")
            return None
        except subprocess.CalledProcessError as e:
            logger.warning(f"Fabric analysis failed for pattern {pattern}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in Fabric analysis: {e}")
            return None
    
    def analyze_transcript(self, transcript_file: Path, video_metadata: Dict) -> Dict:
        """Analyze a single transcript file with all patterns."""
        logger.info(f"Analyzing transcript: {transcript_file.name}")
        
        # Extract clean text
        clean_text = self.clean_transcript_text(transcript_file)
        if not clean_text:
            logger.warning(f"No text extracted from {transcript_file}")
            return {}
        
        # Analyze with each pattern
        analysis_results = {
            'video_id': transcript_file.stem,
            'transcript_file': str(transcript_file),
            'text_length': len(clean_text),
            'word_count': len(clean_text.split()),
            'metadata': video_metadata,
            'analysis': {}
        }
        
        for pattern_name, pattern_id in self.patterns.items():
            logger.info(f"  Running pattern: {pattern_name}")
            result = self.analyze_with_fabric(clean_text, pattern_id)
            
            if result:
                analysis_results['analysis'][pattern_name] = result
                logger.info(f"    ✓ {pattern_name} completed")
            else:
                logger.warning(f"    ✗ {pattern_name} failed")
                analysis_results['analysis'][pattern_name] = None
        
        return analysis_results
    
    def create_custom_patterns(self):
        """Create custom Fabric patterns for horror story analysis if they don't exist."""
        patterns_dir = Path.home() / ".config" / "fabric" / "patterns"
        
        # Horror story hook extraction pattern
        hook_pattern_dir = patterns_dir / "extract_story_hooks"
        hook_pattern_dir.mkdir(parents=True, exist_ok=True)
        
        hook_system_prompt = """# IDENTITY
You are an expert in horror storytelling and audience engagement. You analyze how successful horror stories grab and maintain audience attention.

# GOAL
Extract and analyze the opening hooks and attention-grabbing techniques used in horror stories.

# STEPS
1. Identify the opening hook (first 30-60 seconds of content)
2. Analyze what makes it compelling
3. Look for tension-building techniques
4. Note any immediate mystery or threat establishment
5. Identify pacing and timing of the hook

# OUTPUT
- **Hook Text**: The exact opening lines that serve as the hook
- **Hook Type**: (Mystery, Immediate Threat, Personal Stakes, Atmospheric, etc.)
- **Engagement Techniques**: Specific methods used to grab attention
- **Timing**: How quickly the hook appears
- **Effectiveness**: What makes this hook work for horror audiences
- **Pattern**: The structural pattern of the opening"""
        
        # Write the hook pattern system prompt
        with open(hook_pattern_dir / "system.md", "w") as f:
            f.write(hook_system_prompt)
        
        # Pacing analysis pattern
        pacing_pattern_dir = patterns_dir / "analyze_pacing_structure"
        pacing_pattern_dir.mkdir(parents=True, exist_ok=True)
        
        pacing_system_prompt = """# IDENTITY
You are a horror narrative expert specializing in story pacing and tension management.

# GOAL
Analyze the pacing structure of horror stories to identify successful tension patterns.

# STEPS
1. Break down the story into acts/segments
2. Identify tension peaks and valleys
3. Note pacing changes and their triggers
4. Analyze buildup and release patterns
5. Look for climax timing and resolution structure

# OUTPUT
- **Story Structure**: 3-act breakdown with timing
- **Tension Curve**: Peaks and valleys throughout the story
- **Pacing Techniques**: How tension is built and released
- **Climax Timing**: When and how the main climax occurs
- **Audience Retention**: Techniques to maintain engagement
- **Pattern Formula**: Repeatable structure for similar stories"""
        
        with open(pacing_pattern_dir / "system.md", "w") as f:
            f.write(pacing_system_prompt)
        
        # Horror elements extraction pattern
        horror_pattern_dir = patterns_dir / "extract_horror_elements"
        horror_pattern_dir.mkdir(parents=True, exist_ok=True)
        
        horror_system_prompt = """# IDENTITY
You are a horror genre expert who understands what elements create fear and engagement in audiences.

# GOAL
Extract and categorize the horror elements that make stories effective and engaging.

# STEPS
1. Identify specific horror sub-genres present
2. Catalog fear-inducing elements used
3. Note psychological vs physical horror techniques
4. Analyze character development and relatability
5. Look for unique or creative horror elements

# OUTPUT
- **Horror Sub-genres**: (Psychological, Supernatural, Body Horror, etc.)
- **Fear Elements**: Specific techniques used to create fear
- **Psychological Techniques**: Mind-based horror approaches
- **Atmosphere Building**: Environmental and mood techniques
- **Character Elements**: How characters enhance horror
- **Unique Aspects**: What makes this story stand out
- **Effectiveness Rating**: How well these elements work together"""
        
        with open(horror_pattern_dir / "system.md", "w") as f:
            f.write(horror_system_prompt)
        
        logger.info("Custom Fabric patterns created")
    
    def analyze_all_transcripts(self, metadata_file: str = "research/analysis_summary.json"):
        """Analyze all available transcripts."""
        if not self.check_fabric_available():
            return {}
        
        # Create custom patterns
        self.create_custom_patterns()
        
        # Load metadata
        metadata = {}
        if Path(metadata_file).exists():
            with open(metadata_file, 'r') as f:
                analysis_data = json.load(f)
                
            # Extract video metadata
            for channel_data in analysis_data.get('channels', {}).values():
                for video in channel_data.get('videos', []):
                    metadata[video['id']] = video
        
        # Find transcript files
        transcript_files = list(self.input_dir.glob("*.vtt"))
        if not transcript_files:
            logger.warning(f"No VTT transcript files found in {self.input_dir}")
            return {}
        
        logger.info(f"Found {len(transcript_files)} transcript files to analyze")
        
        # Analyze each transcript
        all_results = {
            'analysis_timestamp': str(Path().resolve()),
            'total_transcripts': len(transcript_files),
            'successful_analyses': 0,
            'patterns_used': list(self.patterns.keys()),
            'results': {}
        }
        
        for transcript_file in transcript_files:
            video_id = transcript_file.stem
            video_metadata = metadata.get(video_id, {})
            
            result = self.analyze_transcript(transcript_file, video_metadata)
            
            if result and any(result.get('analysis', {}).values()):
                all_results['results'][video_id] = result
                all_results['successful_analyses'] += 1
                
                # Save individual result
                output_file = self.output_dir / f"{video_id}_analysis.json"
                with open(output_file, 'w') as f:
                    json.dump(result, f, indent=2)
        
        # Save summary
        summary_file = self.output_dir / "fabric_analysis_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(all_results, f, indent=2)
        
        logger.info(f"Analysis complete. {all_results['successful_analyses']} successful analyses.")
        logger.info(f"Results saved to {summary_file}")
        
        return all_results


def main():
    parser = argparse.ArgumentParser(description='Fabric AI Horror Story Pattern Analyzer')
    parser.add_argument('--transcripts', default='research/transcripts',
                       help='Directory containing transcript files')
    parser.add_argument('--fabric-analysis', action='store_true',
                       help='Run Fabric analysis on transcripts')
    parser.add_argument('--pattern', 
                       help='Run specific pattern (extract_story_hooks, analyze_pacing_structure, extract_horror_elements)')
    parser.add_argument('--output', default='research/fabric_analysis',
                       help='Output directory for analysis results')
    
    args = parser.parse_args()
    
    analyzer = FabricAnalyzer(args.transcripts, args.output)
    
    if args.fabric_analysis:
        results = analyzer.analyze_all_transcripts()
        
        print(f"\nFabric Analysis Summary:")
        print(f"Total transcripts: {results.get('total_transcripts', 0)}")
        print(f"Successful analyses: {results.get('successful_analyses', 0)}")
        print(f"Patterns used: {', '.join(results.get('patterns_used', []))}")
    else:
        print("Use --fabric-analysis to start pattern analysis")


if __name__ == '__main__':
    main()