#!/usr/bin/env python3
"""
Horror Story Generator for YouTube Compilations
Generates 8-10 stories using Claude Code with revenue-optimized prompts
"""

import json
import os
import random
import subprocess
import tempfile
import time
from datetime import datetime

class HorrorStoryGenerator:
    def __init__(self):
        # Random story component lists for infinite variety
        self.jobs = [
            "night security guard", "overnight stocker", "night desk clerk", "graveyard shift dispatcher",
            "night janitor", "overnight gas station attendant", "night shift warehouse worker", 
            "cemetery groundskeeper", "overnight radio DJ", "night shift hotel maintenance",
            "overnight parking attendant", "night shift factory worker", "24-hour diner cook",
            "overnight vet clinic assistant", "night shift call center operator", "graveyard shift nurse",
            "overnight delivery driver", "night shift airport baggage handler", "24-hour laundromat attendant",
            "overnight tow truck operator", "night shift subway operator", "graveyard shift postal worker",
            "overnight casino dealer", "night shift water treatment operator", "24-hour gym front desk",
            "overnight freight loader", "night shift toll booth operator", "graveyard shift newspaper printer"
        ]
        
        self.places = [
            "office building downtown", "24-hour grocery store", "budget motel off the highway",
            "taxi company dispatch center", "medical clinic", "truck stop on Route 66",
            "distribution center", "old cemetery outside town", "small-town radio station",
            "old downtown hotel", "shopping mall parking garage", "chemical plant",
            "all-night diner on the interstate", "veterinary emergency clinic", "call center",
            "county hospital", "package sorting facility", "airport terminal",
            "coin-operated laundromat", "auto impound lot", "subway maintenance tunnel",
            "main post office", "riverboat casino", "water treatment facility",
            "24-hour fitness center", "freight yard", "highway toll plaza",
            "newspaper printing plant", "storage facility", "lumber yard",
            "industrial bakery", "recycling center", "power substation"
        ]
        
        self.time_periods = [
            "Monday night shift", "Tuesday night", "Wednesday evening", "Thursday night shift", 
            "Friday night", "Saturday night", "Sunday evening", "late Monday night",
            "Tuesday graveyard shift", "Wednesday night", "Thursday evening", "Friday graveyard",
            "Saturday evening", "Sunday night shift"
        ]
        
        self.elements = [
            "late visitor with suspicious behavior", "customer who never leaves", "guest with disturbing requests",
            "driver reporting strange passenger", "someone in the building after hours", "trucker with unsettling cargo",
            "delivery that shouldn't exist", "visitor who comes every week", "caller who knows too much",
            "guest complaint about room that doesn't exist", "maintenance request for non-existent area",
            "coworker with disturbing habits", "regular customer acting strangely", "unexpected after-hours visitor",
            "emergency call that doesn't make sense", "delivery to wrong address", "equipment malfunction with human cause",
            "security footage showing impossible events", "phone calls from disconnected numbers",
            "supervisor with secret instructions", "client with unusual requests", "vendor making odd deliveries",
            "inspection by unknown authority", "lost person with suspicious story", "accident that seems planned"
        ]
        
        self.word_lengths = ["1300", "1350", "1400", "1450", "1500", "1550"]
        self.time_ranges = ["9-11", "10-12", "11-13", "10-11", "11-12", "12-14"]
    
    def create_prompt(self, setting):
        """Create the horror story prompt with specific setting variables"""
        
        prompt = f"""Create a first-person horror story of approximately {setting['length']} words that could be narrated in {setting['minutes']} minutes.

REQUIREMENTS:
- Write in first person ("I" perspective)
- Frame as a "true story" the narrator experienced
- Set in a realistic, relatable location: workplace
- Include specific, authentic details that make it believable
- Build tension gradually through normal situations becoming wrong
- Use past tense narration
- End with lasting impact on narrator ("I still..." or "To this day...")
- Establish workplace/setting routine before introducing horror element
- Include multiple "lasting impact" reflections throughout the ending

SETTING PROMPT:
I worked as a {setting['job']} at {setting['place']}. Describe 2-3 typical work routines and normal details about the job before the incident. What started as an ordinary {setting['time_period']} turned into something I'll never forget. The story should involve {setting['element']} and focus on human antagonists or realistic threats with subtle wrongness.

WORKPLACE DETAIL REQUIREMENTS:
- Specific job procedures, equipment, or daily tasks
- Names of coworkers, supervisors, or regular customers (if applicable)
- Physical layout details of the workplace
- Normal schedule, break routines, or typical interactions

ENDING IMPACT REQUIREMENTS:
- Include 2-3 different "I still..." or "To this day..." statements
- Mention specific triggers that bring back memories
- Describe how the experience changed narrator's behavior or perspective
- End with an unsettling final thought or ongoing fear

TONE: Believable, personal account with authentic details. Should feel like it could really happen.

EXAMPLE OPENING STYLE: "I never really thought much about [relevant workplace detail] until that {setting['time_period'].split()[0]} in [month]. I'd been working as a {setting['job']} for [time period] when..."

Generate the complete story now."""

        return prompt
    
    def generate_random_setting(self):
        """Generate completely random story setting for infinite variety"""
        return {
            "job": random.choice(self.jobs),
            "place": random.choice(self.places),
            "time_period": random.choice(self.time_periods),
            "element": random.choice(self.elements),
            "length": random.choice(self.word_lengths),
            "minutes": random.choice(self.time_ranges)
        }
    
    def generate_story(self, setting, story_num):
        """Generate a single story using Claude Code CLI"""
        
        print(f"Generating story {story_num}: {setting['job']} at {setting['place']}...")
        
        prompt = self.create_prompt(setting)
        
        try:
            # Use Claude Code command with --print and pass prompt via stdin
            cmd = [
                'claude', 
                '--print',  # Non-interactive mode
                '--model', 'opus'  # Latest Opus model
            ]
            
            print(f"🤖 Running Claude Code with Opus...")
            result = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=180)
            
            if result.returncode != 0:
                print(f"❌ Claude Code error:")
                print(f"   Return code: {result.returncode}")
                print(f"   Stderr: {result.stderr}")
                print(f"   Stdout: {result.stdout}")
                return None
            
            story_content = result.stdout.strip()
            
            if not story_content:
                print(f"❌ No content generated for story {story_num}")
                return None
            
            # Create story metadata
            story_data = {
                "story_number": story_num,
                "setting": setting,
                "generated_at": datetime.now().isoformat(),
                "word_count": len(story_content.split()),
                "content": story_content,
                "model": "claude-4.1-opus"
            }
            
            print(f"✅ Story {story_num} generated ({story_data['word_count']} words)")
            return story_data
            
        except subprocess.TimeoutExpired:
            print(f"⏱️ Timeout generating story {story_num} - retrying...")
            return None
        except Exception as e:
            print(f"❌ Error generating story {story_num}: {str(e)}")
            return None
    
    def save_stories(self, stories, compilation_name):
        """Save all generated stories to files"""
        
        # Create output directory in tests folder for testing
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Go up one level from scripts/
        output_dir = os.path.join(base_dir, "tests", compilation_name)
        os.makedirs(output_dir, exist_ok=True)
        
        # Save individual stories
        for story in stories:
            if story:
                filename = f"story_{story['story_number']:02d}_{story['setting']['job'].replace(' ', '_')}.md"
                filepath = os.path.join(output_dir, filename)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(f"# Story {story['story_number']}: {story['setting']['job'].title()}\n\n")
                    f.write(f"**Setting**: {story['setting']['place']}\n")
                    f.write(f"**Target Length**: {story['setting']['minutes']} minutes\n")
                    f.write(f"**Word Count**: {story['word_count']} words\n")
                    f.write(f"**Generated**: {story['generated_at']}\n\n")
                    f.write("---\n\n")
                    f.write(story['content'])
        
        # Save compilation metadata
        compilation_data = {
            "name": compilation_name,
            "generated_at": datetime.now().isoformat(),
            "total_stories": len([s for s in stories if s]),
            "total_words": sum(s['word_count'] for s in stories if s),
            "estimated_runtime_minutes": sum(int(s['setting']['minutes'].split('-')[1]) for s in stories if s),
            "stories": [
                {
                    "number": s['story_number'],
                    "job": s['setting']['job'],
                    "place": s['setting']['place'],
                    "word_count": s['word_count'],
                    "filename": f"story_{s['story_number']:02d}_{s['setting']['job'].replace(' ', '_')}.md"
                } for s in stories if s
            ]
        }
        
        with open(os.path.join(output_dir, 'compilation_metadata.json'), 'w') as f:
            json.dump(compilation_data, f, indent=2)
        
        return output_dir, compilation_data
    
    def generate_compilation(self, num_stories=8, compilation_name=None):
        """Generate a complete story compilation"""
        
        if compilation_name is None:
            compilation_name = f"horror_compilation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        print(f"\n🎬 Generating Horror Story Compilation: {compilation_name}")
        print(f"📝 Target: {num_stories} stories")
        print("-" * 60)
        
        # Generate completely random settings for infinite variety
        selected_settings = [self.generate_random_setting() for _ in range(num_stories)]
        
        stories = []
        for i, setting in enumerate(selected_settings, 1):
            story = self.generate_story(setting, i)
            stories.append(story)
            
            # Add delay between requests
            if i < len(selected_settings):
                print("⏱️  Waiting 3 seconds...")
                time.sleep(3)
        
        # Save all stories
        output_dir, metadata = self.save_stories(stories, compilation_name)
        
        # Print summary
        successful_stories = [s for s in stories if s]
        print("\n" + "=" * 60)
        print("📊 COMPILATION COMPLETE")
        print("=" * 60)
        print(f"✅ Generated: {len(successful_stories)}/{num_stories} stories")
        print(f"📝 Total words: {metadata['total_words']:,}")
        print(f"⏱️  Estimated runtime: {metadata['estimated_runtime_minutes']} minutes")
        print(f"📁 Output directory: {output_dir}")
        print("\n📋 Story List:")
        
        for story_info in metadata['stories']:
            print(f"  {story_info['number']:2d}. {story_info['job'].title()} - {story_info['word_count']} words")
        
        return output_dir, metadata


def main():
    """Main execution function"""
    
    # Check if Claude Code CLI is available
    try:
        result = subprocess.run(['claude', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Error: Claude Code CLI not found")
            print("\nPlease ensure Claude Code CLI is installed")
            print("Installation: https://claude.ai/download")
            return
        else:
            print(f"✅ Claude Code CLI found: {result.stdout.strip()}")
    except FileNotFoundError:
        print("❌ Error: Claude Code CLI not found in PATH")
        print("\nPlease ensure Claude Code CLI is installed and in your PATH")
        return
    except Exception as e:
        print(f"❌ Error checking Claude Code CLI: {str(e)}")
        return
    
    # Create generator
    generator = HorrorStoryGenerator()
    
    # Generate compilation
    try:
        num_stories = int(input("How many stories to generate (8-10 recommended): ") or "8")
        compilation_name = input("Compilation name (press Enter for auto-generated): ").strip() or None
        
        print("\n🚀 INFINITE VARIETY ENABLED:")
        print("📊 Possible combinations:")
        jobs_count = len(generator.jobs)
        places_count = len(generator.places)
        elements_count = len(generator.elements)
        total_combinations = jobs_count * places_count * elements_count
        print(f"   {jobs_count} jobs × {places_count} places × {elements_count} elements = {total_combinations:,} unique combinations!")
        print(f"   You could run this script {total_combinations // num_stories:,} times without repeats!\n")
        
        output_dir, metadata = generator.generate_compilation(num_stories, compilation_name)
        
        print(f"\n🎉 Success! Stories saved to: {output_dir}")
        print("\n📋 Next steps:")
        print("1. Review generated stories for quality")
        print("2. Edit/refine any stories as needed")
        print("3. Send to Kokoro-FastAPI for narration")
        print("4. Generate images with Stable Diffusion")
        print("5. Assemble final video compilation")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Generation cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


if __name__ == "__main__":
    main()