# YouTube Horror Story Generator - User Manual

## Quick Reference Commands

### Prerequisites Setup
```bash
# 1. Set up Claude Code OAuth token (one-time setup)
export CLAUDE_CODE_OAUTH_TOKEN="your-token-here"
echo 'export CLAUDE_CODE_OAUTH_TOKEN=your-token-here' >> ~/.zshrc
source ~/.zshrc

# 2. Start Kokoro-FastAPI (required for audio generation)
docker run -d -p 8880:8880 --name kokoro-full ghcr.io/remsky/kokoro-fastapi-cpu:latest

# 3. Check Kokoro is running
curl http://localhost:8880/docs

# 4. Install FFmpeg (if not already installed)
brew install ffmpeg
```

### Main Production Commands

#### 1. Original Random Story Generator
```bash
cd /Users/dustcloudimac/Claude/YouTube-StoryVideo-Generator/scripts
python3 story_generator.py
```
- Generates 8-10 stories using random job/place combinations
- Fast and simple
- Good for testing basic pipeline

#### 2. Creative AI Story Generator (Enhanced)
```bash
cd /Users/dustcloudimac/Claude/YouTube-StoryVideo-Generator/scripts
python3 creative_story_generator.py
```
- AI generates cohesive themes and unique story concepts
- Better quality and creativity
- Evaluates and ranks concepts
- Recommended for production

#### 3. Adaptive Length Manager
```bash
cd /Users/dustcloudimac/Claude/YouTube-StoryVideo-Generator/scripts
python3 adaptive_length_manager.py
```
- Takes generated stories and creates audio using Kokoro
- Measures actual audio lengths
- Optimizes for exactly 180-minute compilations
- Run after creative story generator

#### 4. Full Production Pipeline (Complete Automation)
```bash
cd /Users/dustcloudimac/Claude/YouTube-StoryVideo-Generator/scripts
python3 production_pipeline.py
```
- Complete end-to-end automation
- Includes creative generation + length optimization
- Production-ready output
- Comprehensive reporting

## Detailed Usage Guide

### Getting Started

1. **First-time setup** (run once):
```bash
# Navigate to project
cd /Users/dustcloudimac/Claude/YouTube-StoryVideo-Generator

# Set up environment
export CLAUDE_CODE_OAUTH_TOKEN="your-actual-token"
echo 'export CLAUDE_CODE_OAUTH_TOKEN=your-actual-token' >> ~/.zshrc

# Start Kokoro (keep running)
docker run -d -p 8880:8880 --name kokoro-full ghcr.io/remsky/kokoro-fastapi-cpu:latest
```

2. **Daily usage** (each time you want to generate content):
```bash
# Option A: Quick test (3 stories)
python3 scripts/creative_story_generator.py
# When prompted: Target=3, Buffer=1

# Option B: Full production (8 stories)
python3 scripts/production_pipeline.py
# Select option 1 for full production
```

### Understanding Output Locations

All generated content goes to `/tests/` directory:

```
tests/
├── creative_horror_compilation_YYYYMMDD_HHMMSS/
│   ├── story_01_title.md              # Individual stories
│   ├── story_02_title.md
│   ├── creative_compilation_metadata.json
│   └── final_compilation/             # After length optimization
│       ├── final_compilation_metadata.json
│       ├── compilation_playlist.txt   # For video assembly
│       ├── assembly_instructions.md
│       └── production_summary.json
```

### Production Workflow

#### For Quick Testing (3 stories):
1. `python3 scripts/creative_story_generator.py`
2. Enter: Target=3, Buffer=1
3. Wait ~10 minutes for generation
4. Review stories in `/tests/creative_horror_compilation_*/`

#### For Full Production (8 stories, 180 minutes):
1. `python3 scripts/production_pipeline.py`
2. Select option "1" (Full Production Run)
3. Wait ~30-45 minutes for complete pipeline
4. Final output ready in `/tests/.../final_compilation/`

#### Manual Step-by-Step:
1. `python3 scripts/creative_story_generator.py` (generate stories)
2. `python3 scripts/adaptive_length_manager.py` (optimize length)
3. Follow assembly instructions in `assembly_instructions.md`

## Troubleshooting

### Common Issues

**"Invalid API key · Please run /login"**
```bash
export CLAUDE_CODE_OAUTH_TOKEN="your-token-here"
# Make sure token is correct and not expired
```

**"Kokoro-FastAPI not running"**
```bash
# Check if running
docker ps | grep kokoro

# Start if not running
docker run -d -p 8880:8880 --name kokoro-full ghcr.io/remsky/kokoro-fastapi-cpu:latest

# If already exists but stopped
docker start kokoro-full
```

**"ffmpeg not found"**
```bash
brew install ffmpeg
```

**"Theme generation error: timeout"**
- Try quick test mode first (3 stories instead of 8)
- Check your internet connection
- Restart and try again

**JSON parsing errors**
- Usually means Claude returned non-JSON output
- Try running the command again
- Use quick test mode to debug

### Performance Tips

1. **For development/testing**: Use 3-4 stories max
2. **For production**: Use 8 stories with 2-3 buffer
3. **Memory usage**: Each story generation uses ~1-2GB RAM briefly
4. **Time estimates**:
   - 3 stories: ~10 minutes total
   - 8 stories: ~30-45 minutes total

### Output Quality Checks

After generation, verify:
- [ ] Stories are 1200-1800 words each
- [ ] All stories follow first-person "true story" format
- [ ] Audio files generated successfully (if using length manager)
- [ ] Total duration close to 180 minutes (if full pipeline)
- [ ] Stories are thematically consistent

## Advanced Usage

### Custom Configurations

```bash
# Creative generator with custom counts
python3 scripts/creative_story_generator.py
# Enter custom target and buffer numbers

# Production pipeline with custom options
python3 scripts/production_pipeline.py
# Select option 3 for custom configuration
```

### Manual Audio Assembly

If you have the final compilation files:

```bash
cd /path/to/final_compilation/

# Create silence file
ffmpeg -f lavfi -i anullsrc=r=44100:cl=stereo -t 45 -acodec mp3 silence_45s.wav

# Assemble final compilation
ffmpeg -f concat -safe 0 -i compilation_playlist.txt -c copy final_horror_compilation.mp3
```

### Integration with Other Tools

- **Stable Diffusion**: Use story titles/concepts for image generation
- **Video Editing**: Import audio + images to create final videos  
- **YouTube**: Upload final MP3 or convert to video format

## GitHub Repository

- **URL**: https://github.com/Costa318/YouTube-StoryVideo-Generator
- **Issues**: Report bugs and request features
- **Updates**: Pull latest changes with `git pull`

## Support

If you encounter issues:
1. Check this manual first
2. Review error messages carefully  
3. Try quick test mode before full production
4. Check prerequisites are properly set up
5. Restart Docker containers if needed

---

*Last updated: 2025-08-28*