#!/usr/bin/env python3
"""
Adaptive Length Management System
Measures actual audio lengths and intelligently selects stories for exact 180-minute compilations
"""

import json
import os
import subprocess
import requests
import time
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import itertools

class AdaptiveLengthManager:
    def __init__(self, kokoro_url: str = "http://localhost:8880"):
        self.kokoro_url = kokoro_url
        self.target_duration = 180 * 60  # 180 minutes in seconds
        self.story_gap = 45  # 45 seconds between stories
        
    def check_kokoro_status(self) -> bool:
        """Check if Kokoro-FastAPI is running"""
        try:
            response = requests.get(f"{self.kokoro_url}/docs", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def generate_audio_batch(self, stories: List[Dict], voice: str = "af_sarah") -> List[Dict]:
        """Generate audio for all stories using Kokoro-FastAPI"""
        
        if not self.check_kokoro_status():
            print("❌ Kokoro-FastAPI not running at http://localhost:8880")
            print("   Please start Kokoro with: docker run -d -p 8880:8880 --name kokoro-full ghcr.io/remsky/kokoro-fastapi-cpu:latest")
            return []
        
        print(f"🎙️  Generating audio for {len(stories)} stories using Kokoro...")
        audio_stories = []
        
        for i, story in enumerate(stories, 1):
            if not story:
                continue
                
            print(f"   Processing story {i}/{len(stories)}: {story['concept']['title'][:30]}...")
            
            # Prepare request for Kokoro
            audio_request = {
                "model": "kokoro",
                "input": story['content'],
                "voice": voice,
                "response_format": "mp3",
                "speed": 1.0
            }
            
            try:
                # Generate audio
                response = requests.post(f"{self.kokoro_url}/v1/audio/speech", json=audio_request, timeout=300)
                
                if response.status_code == 200:
                    # Save audio file
                    audio_filename = f"story_{story['story_number']:02d}_audio.mp3"
                    audio_path = os.path.join("/tmp", audio_filename)
                    
                    with open(audio_path, 'wb') as f:
                        f.write(response.content)
                    
                    # Measure audio duration
                    duration = self.measure_audio_duration(audio_path)
                    
                    if duration:
                        audio_story = story.copy()
                        audio_story.update({
                            "audio_path": audio_path,
                            "audio_duration_seconds": duration,
                            "audio_duration_minutes": duration / 60,
                            "voice_used": voice
                        })
                        audio_stories.append(audio_story)
                        
                        print(f"   ✅ Generated: {duration/60:.1f} minutes")
                    else:
                        print(f"   ❌ Could not measure audio duration")
                        
                else:
                    print(f"   ❌ Kokoro error: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Audio generation error: {e}")
                
            # Small delay between requests
            if i < len(stories):
                time.sleep(2)
        
        return audio_stories
    
    def measure_audio_duration(self, audio_path: str) -> Optional[float]:
        """Measure actual audio duration using ffprobe"""
        try:
            cmd = [
                'ffprobe', 
                '-v', 'quiet', 
                '-show_entries', 'format=duration', 
                '-of', 'default=noprint_wrappers=1:nokey=1', 
                audio_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return float(result.stdout.strip())
            else:
                print(f"   ❌ ffprobe error: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"   ❌ Duration measurement error: {e}")
            return None
    
    def find_optimal_story_combination(self, audio_stories: List[Dict], target_stories: int = 8) -> Optional[List[Dict]]:
        """Find the best combination of stories that gets closest to 180 minutes"""
        
        if len(audio_stories) < target_stories:
            print(f"❌ Not enough audio stories ({len(audio_stories)} < {target_stories})")
            return None
        
        print(f"🧮 Finding optimal combination of {target_stories} stories from {len(audio_stories)} available...")
        
        best_combination = None
        best_score = float('inf')
        best_total_duration = 0
        
        # Try all combinations of target_stories from available stories
        for combination in itertools.combinations(audio_stories, target_stories):
            # Calculate total duration including gaps
            story_duration = sum(story['audio_duration_seconds'] for story in combination)
            gap_duration = (len(combination) - 1) * self.story_gap
            total_duration = story_duration + gap_duration
            
            # Score based on how close to target (lower is better)
            score = abs(total_duration - self.target_duration)
            
            if score < best_score:
                best_score = score
                best_combination = list(combination)
                best_total_duration = total_duration
        
        if best_combination:
            minutes_diff = (best_total_duration - self.target_duration) / 60
            print(f"✅ Optimal combination found:")
            print(f"   Target: 180.0 minutes")
            print(f"   Achieved: {best_total_duration/60:.1f} minutes")
            print(f"   Difference: {minutes_diff:+.1f} minutes")
            
            return best_combination
        
        return None
    
    def create_final_compilation(self, selected_stories: List[Dict], compilation_data: Dict) -> Dict:
        """Create final compilation with selected stories and timing data"""
        
        # Sort stories by original story number for logical flow
        selected_stories.sort(key=lambda x: x['story_number'])
        
        # Calculate final timing
        total_story_duration = sum(story['audio_duration_seconds'] for story in selected_stories)
        total_gap_duration = (len(selected_stories) - 1) * self.story_gap
        final_duration = total_story_duration + total_gap_duration
        
        final_compilation = {
            "name": compilation_data["name"] + "_final",
            "original_compilation": compilation_data["name"],
            "generated_at": datetime.now().isoformat(),
            "selection_method": "adaptive_length_optimization",
            "target_duration_seconds": self.target_duration,
            "actual_duration_seconds": final_duration,
            "duration_difference_seconds": final_duration - self.target_duration,
            "story_gap_seconds": self.story_gap,
            "selected_stories_count": len(selected_stories),
            "total_story_duration": total_story_duration,
            "total_gap_duration": total_gap_duration,
            "stories": []
        }
        
        # Add stories with timing information
        current_start_time = 0
        for i, story in enumerate(selected_stories):
            story_info = {
                "compilation_position": i + 1,
                "original_story_number": story['story_number'],
                "title": story['concept']['title'],
                "audio_path": story['audio_path'],
                "duration_seconds": story['audio_duration_seconds'],
                "duration_minutes": story['audio_duration_minutes'],
                "start_time_seconds": current_start_time,
                "start_time_formatted": self.format_time(current_start_time),
                "end_time_seconds": current_start_time + story['audio_duration_seconds'],
                "end_time_formatted": self.format_time(current_start_time + story['audio_duration_seconds']),
                "concept": story['concept'],
                "word_count": story['word_count']
            }
            
            final_compilation["stories"].append(story_info)
            current_start_time += story['audio_duration_seconds'] + self.story_gap
        
        return final_compilation
    
    def format_time(self, seconds: float) -> str:
        """Format seconds as HH:MM:SS"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    def save_final_compilation(self, final_compilation: Dict, base_output_dir: str) -> str:
        """Save the final optimized compilation"""
        
        final_dir = os.path.join(base_output_dir, "final_compilation")
        os.makedirs(final_dir, exist_ok=True)
        
        # Save final compilation metadata
        metadata_path = os.path.join(final_dir, "final_compilation_metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(final_compilation, f, indent=2)
        
        # Create playlist file for easy assembly
        playlist_path = os.path.join(final_dir, "compilation_playlist.txt")
        with open(playlist_path, 'w') as f:
            f.write("# Final Horror Compilation Playlist\n")
            f.write(f"# Total Duration: {final_compilation['actual_duration_seconds']/60:.1f} minutes\n")
            f.write(f"# Target: {final_compilation['target_duration_seconds']/60:.1f} minutes\n\n")
            
            for story in final_compilation["stories"]:
                f.write(f"# Story {story['compilation_position']}: {story['title']}\n")
                f.write(f"# Start: {story['start_time_formatted']} | Duration: {story['duration_minutes']:.1f}min\n")
                f.write(f"file '{story['audio_path']}'\n")
                
                # Add silence between stories (except after last story)
                if story['compilation_position'] < len(final_compilation["stories"]):
                    f.write(f"# Gap: {final_compilation['story_gap_seconds']} seconds\n")
                    f.write(f"file 'silence_{final_compilation['story_gap_seconds']}s.wav'\n")
                f.write("\n")
        
        # Create assembly instructions
        instructions_path = os.path.join(final_dir, "assembly_instructions.md")
        with open(instructions_path, 'w') as f:
            f.write("# Final Compilation Assembly Instructions\n\n")
            f.write(f"## Compilation Details\n")
            f.write(f"- **Total Duration**: {final_compilation['actual_duration_seconds']/60:.1f} minutes\n")
            f.write(f"- **Target Duration**: {final_compilation['target_duration_seconds']/60:.1f} minutes\n")
            f.write(f"- **Difference**: {final_compilation['duration_difference_seconds']/60:+.1f} minutes\n")
            f.write(f"- **Stories**: {final_compilation['selected_stories_count']}\n")
            f.write(f"- **Gap Between Stories**: {final_compilation['story_gap_seconds']} seconds\n\n")
            
            f.write("## Story Timeline\n")
            for story in final_compilation["stories"]:
                f.write(f"- **{story['start_time_formatted']}-{story['end_time_formatted']}**: {story['title']} ({story['duration_minutes']:.1f}min)\n")
            
            f.write("\n## Assembly Commands\n")
            f.write("### Generate silence file:\n")
            f.write(f"```bash\nffmpeg -f lavfi -i anullsrc=r=44100:cl=stereo -t {final_compilation['story_gap_seconds']} -acodec mp3 silence_{final_compilation['story_gap_seconds']}s.wav\n```\n\n")
            f.write("### Concatenate final compilation:\n")
            f.write(f"```bash\nffmpeg -f concat -safe 0 -i compilation_playlist.txt -c copy final_horror_compilation.mp3\n```\n")
        
        return final_dir
    
    def process_compilation(self, compilation_data: Dict, base_output_dir: str) -> Optional[str]:
        """Complete adaptive length management process"""
        
        print(f"\n🎯 Starting Adaptive Length Management")
        print(f"📊 Input: {len(compilation_data['stories'])} stories")
        print(f"🎯 Target: 180 minutes (3 hours)")
        print("-" * 60)
        
        # Step 1: Generate audio for all stories
        audio_stories = self.generate_audio_batch(compilation_data['stories'])
        
        if not audio_stories:
            print("❌ No audio stories generated")
            return None
        
        # Step 2: Find optimal combination
        optimal_stories = self.find_optimal_story_combination(audio_stories, target_stories=8)
        
        if not optimal_stories:
            print("❌ Could not find optimal story combination")
            return None
        
        # Step 3: Create final compilation
        final_compilation = self.create_final_compilation(optimal_stories, compilation_data)
        
        # Step 4: Save final compilation
        final_dir = self.save_final_compilation(final_compilation, base_output_dir)
        
        print(f"\n🎉 Adaptive Length Management Complete!")
        print(f"📁 Final compilation saved to: {final_dir}")
        
        return final_dir

def main():
    """Test adaptive length management with existing compilation"""
    
    manager = AdaptiveLengthManager()
    
    # Get latest compilation from tests directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    tests_dir = os.path.join(base_dir, "tests")
    
    # Find most recent compilation directory
    compilations = [d for d in os.listdir(tests_dir) if d.startswith("creative_horror_compilation")]
    if not compilations:
        print("❌ No creative compilations found. Run creative_story_generator.py first.")
        return
    
    latest_compilation = sorted(compilations)[-1]
    compilation_dir = os.path.join(tests_dir, latest_compilation)
    
    # Load compilation metadata
    metadata_path = os.path.join(compilation_dir, "creative_compilation_metadata.json")
    if not os.path.exists(metadata_path):
        print("❌ Compilation metadata not found")
        return
    
    with open(metadata_path, 'r') as f:
        compilation_data = json.load(f)
    
    print(f"📂 Processing compilation: {latest_compilation}")
    
    # Process with adaptive length management
    final_dir = manager.process_compilation(compilation_data, compilation_dir)
    
    if final_dir:
        print(f"\n✅ Success! Check {final_dir} for final compilation files")

if __name__ == "__main__":
    main()