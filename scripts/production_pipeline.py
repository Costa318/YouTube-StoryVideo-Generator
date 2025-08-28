#!/usr/bin/env python3
"""
Production Pipeline Integration
End-to-end automation from creative concepts to final YouTube-ready compilation
"""

import json
import os
import subprocess
import time
from datetime import datetime
from typing import Dict, Optional

from creative_story_generator import CreativeHorrorGenerator
from adaptive_length_manager import AdaptiveLengthManager

class ProductionPipeline:
    def __init__(self):
        self.creative_generator = CreativeHorrorGenerator()
        self.length_manager = AdaptiveLengthManager()
        
    def run_full_pipeline(self, target_stories: int = 8, buffer_stories: int = 3) -> Optional[str]:
        """Run complete production pipeline from concepts to final compilation"""
        
        pipeline_start = datetime.now()
        pipeline_name = f"horror_production_{pipeline_start.strftime('%Y%m%d_%H%M%S')}"
        
        print("🎬" + "="*70)
        print("🎬 YOUTUBE HORROR STORY GENERATOR - PRODUCTION PIPELINE")
        print("🎬" + "="*70)
        print(f"🎯 Target: {target_stories} stories for 180-minute compilation")
        print(f"🔄 Buffer: {buffer_stories} extra stories for optimization")
        print(f"📅 Started: {pipeline_start.strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 70)
        
        try:
            # Phase 1: Creative Story Generation
            print("\n📝 PHASE 1: CREATIVE STORY GENERATION")
            print("=" * 50)
            
            output_dir, compilation_data = self.creative_generator.generate_creative_compilation(
                target_stories=target_stories, 
                buffer_stories=buffer_stories
            )
            
            if not output_dir or not compilation_data:
                print("❌ Phase 1 failed: Creative story generation")
                return None
            
            print(f"✅ Phase 1 complete: {len(compilation_data['stories'])} stories generated")
            
            # Phase 2: Adaptive Length Management
            print("\n🎙️ PHASE 2: ADAPTIVE LENGTH MANAGEMENT")
            print("=" * 50)
            
            final_dir = self.length_manager.process_compilation(compilation_data, output_dir)
            
            if not final_dir:
                print("❌ Phase 2 failed: Adaptive length management")
                return None
            
            print(f"✅ Phase 2 complete: Optimized compilation ready")
            
            # Phase 3: Production Summary
            print("\n📊 PRODUCTION SUMMARY")
            print("=" * 50)
            
            self.generate_production_summary(final_dir, pipeline_start, pipeline_name)
            
            pipeline_end = datetime.now()
            total_time = (pipeline_end - pipeline_start).total_seconds() / 60
            
            print(f"\n🎉 PIPELINE COMPLETE!")
            print(f"⏱️  Total time: {total_time:.1f} minutes")
            print(f"📁 Output: {final_dir}")
            print(f"🎬 Ready for YouTube upload!")
            
            return final_dir
            
        except Exception as e:
            print(f"❌ Pipeline error: {e}")
            return None
    
    def generate_production_summary(self, final_dir: str, start_time: datetime, pipeline_name: str):
        """Generate comprehensive production summary"""
        
        # Load final compilation metadata
        metadata_path = os.path.join(final_dir, "final_compilation_metadata.json")
        if not os.path.exists(metadata_path):
            print("❌ Could not load final compilation metadata")
            return
        
        with open(metadata_path, 'r') as f:
            final_data = json.load(f)
        
        # Create production summary
        production_summary = {
            "pipeline_name": pipeline_name,
            "production_start": start_time.isoformat(),
            "production_end": datetime.now().isoformat(),
            "total_production_time_minutes": (datetime.now() - start_time).total_seconds() / 60,
            "final_compilation": {
                "duration_minutes": final_data["actual_duration_seconds"] / 60,
                "target_duration_minutes": final_data["target_duration_seconds"] / 60,
                "duration_accuracy": f"{abs(final_data['duration_difference_seconds'])/60:.1f}min difference",
                "story_count": final_data["selected_stories_count"],
                "story_titles": [story["title"] for story in final_data["stories"]]
            },
            "youtube_optimization": {
                "target_format": "3-hour horror compilation",
                "monetization_strategy": "Ultra-long format for maximum watch hours",
                "estimated_views_needed": "22-25 views per video for monetization threshold",
                "ad_placement_opportunities": f"~{int(final_data['actual_duration_seconds']/480)} mid-roll ads possible"
            },
            "next_steps": [
                "Review final compilation audio quality",
                "Generate atmospheric background images",
                "Create YouTube thumbnail and metadata",
                "Upload and schedule for optimal posting time",
                "Monitor performance and iterate"
            ]
        }
        
        # Save production summary
        summary_path = os.path.join(final_dir, "production_summary.json")
        with open(summary_path, 'w') as f:
            json.dump(production_summary, f, indent=2)
        
        # Display key metrics
        print(f"📊 Final Duration: {final_data['actual_duration_seconds']/60:.1f} minutes")
        print(f"🎯 Target Accuracy: {abs(final_data['duration_difference_seconds'])/60:.1f}min difference")
        print(f"📝 Stories Selected: {final_data['selected_stories_count']}")
        print(f"💰 Ad Opportunities: ~{int(final_data['actual_duration_seconds']/480)} mid-roll ads")
        
    def quick_test_run(self) -> Optional[str]:
        """Quick test run with minimal stories for development/testing"""
        
        print("🧪 QUICK TEST RUN - Development Mode")
        print("-" * 40)
        
        return self.run_full_pipeline(target_stories=3, buffer_stories=2)

def main():
    """Main execution with user options"""
    
    # Check prerequisites
    print("🔍 Checking prerequisites...")
    
    # Check Claude Code CLI
    try:
        result = subprocess.run(['claude', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Claude Code CLI: {result.stdout.strip()}")
        else:
            print("❌ Claude Code CLI not found")
            return
    except FileNotFoundError:
        print("❌ Claude Code CLI not found in PATH")
        return
    
    # Check Kokoro-FastAPI
    import requests
    try:
        response = requests.get("http://localhost:8880/docs", timeout=5)
        if response.status_code == 200:
            print("✅ Kokoro-FastAPI running on localhost:8880")
        else:
            print("❌ Kokoro-FastAPI not responding")
            print("   Start with: docker run -d -p 8880:8880 --name kokoro-full ghcr.io/remsky/kokoro-fastapi-cpu:latest")
            return
    except:
        print("❌ Kokoro-FastAPI not running")
        print("   Start with: docker run -d -p 8880:8880 --name kokoro-full ghcr.io/remsky/kokoro-fastapi-cpu:latest")
        return
    
    # Check ffmpeg
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ FFmpeg available")
        else:
            print("❌ FFmpeg not found")
            return
    except FileNotFoundError:
        print("❌ FFmpeg not found - install with: brew install ffmpeg")
        return
    
    print("\n🚀 All prerequisites met!")
    
    # User options
    pipeline = ProductionPipeline()
    
    print("\n" + "="*50)
    print("PRODUCTION OPTIONS")
    print("="*50)
    print("1. Full Production Run (8 stories + buffer)")
    print("2. Quick Test Run (3 stories + buffer)")
    print("3. Custom Configuration")
    
    try:
        choice = input("\nSelect option (1-3): ").strip()
        
        if choice == "1":
            result = pipeline.run_full_pipeline()
        elif choice == "2":
            result = pipeline.quick_test_run()
        elif choice == "3":
            target = int(input("Target stories (8 recommended): ") or "8")
            buffer = int(input("Buffer stories (3 recommended): ") or "3")
            result = pipeline.run_full_pipeline(target, buffer)
        else:
            print("Invalid option")
            return
        
        if result:
            print(f"\n🎉 SUCCESS! Production pipeline complete.")
            print(f"📁 Final output: {result}")
            print(f"🔗 GitHub: https://github.com/Costa318/YouTube-StoryVideo-Generator")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Production cancelled by user")
    except Exception as e:
        print(f"\n❌ Production error: {str(e)}")

if __name__ == "__main__":
    main()