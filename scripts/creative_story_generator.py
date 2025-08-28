#!/usr/bin/env python3
"""
Enhanced Creative Horror Story Generator
Uses AI to generate creative story concepts instead of mechanical randomization
"""

import json
import os
import subprocess
import tempfile
import time
from datetime import datetime
from typing import List, Dict, Optional

class CreativeHorrorGenerator:
    def __init__(self):
        self.base_template = """Create a first-person horror story of approximately [LENGTH] words that could be narrated in [TARGET_MINUTES] minutes.

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
{setting_description}

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

Generate the complete story now."""

    def generate_compilation_theme(self) -> Dict:
        """Generate a cohesive theme and story concepts using AI"""
        
        theme_prompt = """Create a horror compilation theme with 4 story concepts.

Generate JSON output with this exact structure:
{
  "compilation_theme": "Night shift workplace horror",
  "compilation_title": "4 True Scary Night Shift Stories That Will Keep You Awake", 
  "theme_description": "Stories about night shift workers encountering disturbing people",
  "story_concepts": [
    {
      "concept_id": 1,
      "title": "The Cleaning Crew",
      "job": "night security guard",
      "workplace": "office building", 
      "horror_element": "cleaning crew member with disturbing behavior",
      "unique_hook": "discovers what the cleaner does during breaks",
      "character_details": "new security guard, observant",
      "plot_outline": "Guard notices cleaner acting strangely. Investigates and discovers disturbing truth.",
      "target_words": 1400,
      "estimated_minutes": "10-12"
    },
    {
      "concept_id": 2,
      "title": "The Night Caller",
      "job": "overnight radio DJ",
      "workplace": "small radio station", 
      "horror_element": "frequent caller who knows too much",
      "unique_hook": "caller describes DJ's private life in real time",
      "character_details": "lonely DJ, works alone",
      "plot_outline": "Regular caller begins revealing personal information. DJ realizes they're being watched.",
      "target_words": 1500,
      "estimated_minutes": "11-13"
    },
    {
      "concept_id": 3,
      "title": "Storage Room 12",
      "job": "overnight stocker",
      "workplace": "big box store", 
      "horror_element": "coworker with secret storage room activities",
      "unique_hook": "forbidden storage room used for disturbing purpose",
      "character_details": "college student, needs the job",
      "plot_outline": "New worker discovers coworker accessing restricted area. Investigation reveals horrifying truth.",
      "target_words": 1450,
      "estimated_minutes": "10-12"
    },
    {
      "concept_id": 4,
      "title": "The Regular Customer",
      "job": "night cashier",
      "workplace": "24-hour gas station", 
      "horror_element": "customer who visits every night with strange purchases",
      "unique_hook": "purchases create disturbing pattern over time",
      "character_details": "young cashier, works alone",
      "plot_outline": "Regular customer's purchases become increasingly disturbing. Cashier pieces together the horrifying truth.",
      "target_words": 1400,
      "estimated_minutes": "10-12"
    }
  ]
}"""

        print("🎨 Generating creative compilation theme and story concepts...")
        
        try:
            cmd = ['claude', '--print', '--model', 'opus']
            result = subprocess.run(cmd, input=theme_prompt, capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                print(f"❌ Theme generation error: {result.stderr}")
                return None
                
            # Parse AI response - expect JSON format
            theme_data = json.loads(result.stdout.strip())
            print(f"✅ Generated theme: {theme_data['compilation_title']}")
            print(f"📖 {len(theme_data['story_concepts'])} story concepts created")
            
            return theme_data
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
            print(f"Raw response: {result.stdout[:200]}...")
            return None
        except Exception as e:
            print(f"❌ Theme generation error: {e}")
            return None
    
    def evaluate_story_concepts(self, theme_data: Dict) -> List[Dict]:
        """Use AI to evaluate and rank story concepts for quality"""
        
        concepts_json = json.dumps(theme_data['story_concepts'], indent=2)
        
        evaluation_prompt = f"""Evaluate and rank these horror story concepts for a YouTube compilation.

STORY CONCEPTS:
{concepts_json}

EVALUATION CRITERIA:
- Creativity and uniqueness of premise
- Believability and authenticity potential  
- Horror effectiveness (tension, fear factor)
- Workplace setting authenticity
- Character development potential
- Narrative hook strength

TASKS:
1. Rank all concepts from best (1) to worst
2. Rate each concept 1-10 on overall quality
3. Identify the top 10 concepts for production
4. Explain ranking rationale

OUTPUT FORMAT:
{{
  "rankings": [
    {{
      "rank": 1,
      "concept_id": X,
      "title": "Story title",
      "quality_score": 9,
      "strengths": ["strength1", "strength2"],
      "selected_for_production": true,
      "rationale": "Why this concept ranks here"
    }}
  ],
  "production_recommendations": {{
    "top_concepts": [list of concept_ids for production],
    "suggested_order": [recommended story order for compilation],
    "pacing_notes": "Notes on compilation flow and pacing"
  }}
}}

Evaluate and rank all concepts now."""

        print("📊 Evaluating story concepts for quality and selection...")
        
        try:
            cmd = ['claude', '--print', '--model', 'opus']
            result = subprocess.run(cmd, input=evaluation_prompt, capture_output=True, text=True, timeout=90)
            
            if result.returncode != 0:
                print(f"❌ Evaluation error: {result.stderr}")
                return theme_data['story_concepts'][:10]  # Fallback to first 10
                
            evaluation_data = json.loads(result.stdout.strip())
            
            # Extract top concepts based on evaluation
            top_concept_ids = evaluation_data['production_recommendations']['top_concepts']
            selected_concepts = []
            
            for concept_id in top_concept_ids:
                concept = next((c for c in theme_data['story_concepts'] if c['concept_id'] == concept_id), None)
                if concept:
                    selected_concepts.append(concept)
            
            print(f"✅ Selected {len(selected_concepts)} top concepts for production")
            return selected_concepts
            
        except Exception as e:
            print(f"❌ Evaluation error: {e}")
            # Fallback to first 10 concepts
            return theme_data['story_concepts'][:10]
    
    def generate_creative_story(self, concept: Dict, story_num: int) -> Optional[Dict]:
        """Generate a story based on creative concept instead of random template"""
        
        print(f"Generating story {story_num}: {concept['title']}...")
        
        # Create detailed setting description from concept
        setting_description = f"""I worked as a {concept['job']} at {concept['workplace']}.

CHARACTER BACKGROUND: {concept['character_details']}

STORY CONCEPT: {concept['plot_outline']}

UNIQUE ELEMENTS: {concept['unique_hook']}

HORROR ELEMENT: {concept['horror_element']}

Develop this concept into a complete horror story with authentic workplace details, gradual tension building, and a satisfying conclusion that leaves lasting psychological impact."""
        
        # Fill in the template
        story_prompt = self.base_template.replace('[LENGTH]', str(concept['target_words']))
        story_prompt = story_prompt.replace('[TARGET_MINUTES]', concept['estimated_minutes'])
        story_prompt = story_prompt.replace('{setting_description}', setting_description)
        
        try:
            cmd = ['claude', '--print', '--model', 'opus']
            result = subprocess.run(cmd, input=story_prompt, capture_output=True, text=True, timeout=180)
            
            if result.returncode != 0:
                print(f"❌ Story generation error: {result.stderr}")
                return None
            
            story_content = result.stdout.strip()
            
            if not story_content:
                print(f"❌ No content generated for story {story_num}")
                return None
            
            story_data = {
                "story_number": story_num,
                "concept": concept,
                "generated_at": datetime.now().isoformat(),
                "word_count": len(story_content.split()),
                "content": story_content,
                "model": "claude-4.1-opus"
            }
            
            print(f"✅ Story {story_num} generated ({story_data['word_count']} words)")
            return story_data
            
        except Exception as e:
            print(f"❌ Error generating story {story_num}: {e}")
            return None
    
    def generate_creative_compilation(self, target_stories: int = 8, buffer_stories: int = 2) -> Dict:
        """Generate a complete creative compilation with buffer stories"""
        
        compilation_name = f"creative_horror_compilation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        print(f"\n🎬 Generating Creative Horror Compilation: {compilation_name}")
        print(f"📝 Target: {target_stories} stories + {buffer_stories} buffer stories")
        print("-" * 60)
        
        # Step 1: Generate theme and concepts
        theme_data = self.generate_compilation_theme()
        if not theme_data:
            print("❌ Failed to generate theme")
            return None
        
        # Step 2: Evaluate and select concepts
        selected_concepts = self.evaluate_story_concepts(theme_data)
        total_concepts = min(target_stories + buffer_stories, len(selected_concepts))
        
        # Step 3: Generate stories from selected concepts
        stories = []
        for i, concept in enumerate(selected_concepts[:total_concepts], 1):
            story = self.generate_creative_story(concept, i)
            stories.append(story)
            
            if i < total_concepts:
                print("⏱️  Waiting 3 seconds...")
                time.sleep(3)
        
        # Step 4: Create compilation data
        successful_stories = [s for s in stories if s]
        
        compilation_data = {
            "name": compilation_name,
            "theme_data": theme_data,
            "generated_at": datetime.now().isoformat(),
            "target_stories": target_stories,
            "buffer_stories": buffer_stories,
            "total_generated": len(successful_stories),
            "total_words": sum(s['word_count'] for s in successful_stories),
            "estimated_runtime_minutes": sum(int(s['concept']['estimated_minutes'].split('-')[1]) for s in successful_stories),
            "stories": successful_stories
        }
        
        # Step 5: Save compilation
        output_dir = self.save_creative_compilation(compilation_data)
        
        return output_dir, compilation_data
    
    def save_creative_compilation(self, compilation_data: Dict) -> str:
        """Save creative compilation with enhanced metadata"""
        
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_dir = os.path.join(base_dir, "tests", compilation_data["name"])
        os.makedirs(output_dir, exist_ok=True)
        
        # Save individual stories
        for story in compilation_data["stories"]:
            if story:
                filename = f"story_{story['story_number']:02d}_{story['concept']['title'].lower().replace(' ', '_').replace(',', '')}.md"
                filepath = os.path.join(output_dir, filename)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(f"# Story {story['story_number']}: {story['concept']['title']}\n\n")
                    f.write(f"**Concept**: {story['concept']['unique_hook']}\n")
                    f.write(f"**Job**: {story['concept']['job']}\n")
                    f.write(f"**Workplace**: {story['concept']['workplace']}\n")
                    f.write(f"**Horror Element**: {story['concept']['horror_element']}\n")
                    f.write(f"**Target Length**: {story['concept']['estimated_minutes']} minutes\n")
                    f.write(f"**Word Count**: {story['word_count']} words\n")
                    f.write(f"**Generated**: {story['generated_at']}\n\n")
                    f.write("---\n\n")
                    f.write(story['content'])
        
        # Save enhanced compilation metadata
        with open(os.path.join(output_dir, 'creative_compilation_metadata.json'), 'w') as f:
            json.dump(compilation_data, f, indent=2)
        
        return output_dir

def main():
    """Main execution with creative generation"""
    
    # Check Claude Code CLI
    try:
        result = subprocess.run(['claude', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Error: Claude Code CLI not found")
            return
        else:
            print(f"✅ Claude Code CLI found: {result.stdout.strip()}")
    except FileNotFoundError:
        print("❌ Error: Claude Code CLI not found in PATH")
        return
    
    generator = CreativeHorrorGenerator()
    
    try:
        target_stories = int(input("Target stories for compilation (8-10 recommended): ") or "8")
        buffer_stories = int(input("Buffer stories to generate (2-4 recommended): ") or "2")
        
        print("\n🚀 CREATIVE AI GENERATION ENABLED:")
        print("🎨 AI will generate cohesive themes and unique story concepts")
        print("📊 AI will evaluate and rank concepts for quality")
        print("🎯 AI will create interconnected stories with narrative flow\n")
        
        output_dir, metadata = generator.generate_creative_compilation(target_stories, buffer_stories)
        
        if output_dir and metadata:
            print(f"\n🎉 Success! Creative compilation saved to: {output_dir}")
            print(f"\n📊 COMPILATION SUMMARY:")
            print(f"🎬 Theme: {metadata['theme_data']['compilation_title']}")
            print(f"📝 Stories Generated: {metadata['total_generated']}")
            print(f"📄 Total Words: {metadata['total_words']:,}")
            print(f"⏱️  Estimated Runtime: {metadata['estimated_runtime_minutes']} minutes")
            
            print(f"\n📋 STORY LIST:")
            for story in metadata['stories']:
                if story:
                    concept = story['concept']
                    print(f"  {story['story_number']:2d}. {concept['title']} - {story['word_count']} words")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Generation cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    main()