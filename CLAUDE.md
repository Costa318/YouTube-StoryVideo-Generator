# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This project creates long-form horror story videos for YouTube using a 5-phase automated pipeline. The system integrates existing AI tools (Kokoro-FastAPI, StableDiffusion-Local, N8N, ObsidianKnowledgeBase) to generate 1-2+ hour videos with narration, atmospheric imagery, and background audio. Target: 7 videos per weekly batch production day.

## Development Commands

### Phase 0: YouTube Transcript Analysis
```bash
# Extract transcripts from successful horror story channels (no video download)
python scripts/content_analyzer.py --channels horror_channels.json --extract-transcripts --min-views 100000

# Analyze story patterns using Fabric AI
python scripts/content_analyzer.py --fabric-analysis --pattern extract_story_hooks --transcripts research/transcripts/
python scripts/content_analyzer.py --fabric-analysis --pattern analyze_pacing_structure --transcripts research/transcripts/
python scripts/content_analyzer.py --fabric-analysis --pattern extract_horror_elements --transcripts research/transcripts/

# Generate story templates from successful transcript patterns
python scripts/inspiration_generator.py --transcripts-analysis research/fabric_analysis/ --create-templates

# Correlate story patterns with performance metrics  
python scripts/inspiration_generator.py --correlate-performance --views-threshold 500000 --output research/high_performing_patterns.json
```

### Phase 1: Story Preparation
```bash
# Create story script from inspiration brief
python scripts/story_processor.py --inspiration research/inspiration_briefs/brief_001.json --output ~/Claude/YouTube-Content/horror-stories/

# Generate image prompts and timing from story script
python scripts/story_processor.py --script ~/Claude/YouTube-Content/horror-stories/story_001/script.json --generate-prompts

# Validate story structure and pacing
python scripts/story_processor.py --validate ~/Claude/YouTube-Content/horror-stories/story_001/
```

### Phase 2: Asset Generation
```bash
# Generate narration audio using Kokoro-FastAPI
python scripts/asset_generator.py --narration --story ~/Claude/YouTube-Content/horror-stories/story_001/

# Generate atmospheric images using StableDiffusion-Local
python scripts/asset_generator.py --images --story ~/Claude/YouTube-Content/horror-stories/story_001/

# Generate complete asset library for story
python scripts/asset_generator.py --all --story ~/Claude/YouTube-Content/horror-stories/story_001/

# Quality check generated assets
python scripts/asset_generator.py --validate ~/Claude/YouTube-Content/horror-stories/story_001/assets/
```

### Phase 3: Video Assembly
```bash
# Assemble final video with ffmpeg
python scripts/video_assembler.py --story ~/Claude/YouTube-Content/horror-stories/story_001/

# Preview video with timing validation
python scripts/video_assembler.py --preview --story ~/Claude/YouTube-Content/horror-stories/story_001/

# Generate video with custom transitions
python scripts/video_assembler.py --story story_001 --transition-style fade --duration-per-image 8
```

### Phase 4: Publishing
```bash
# Generate YouTube metadata and thumbnails
python scripts/publisher.py --metadata --story ~/Claude/YouTube-Content/horror-stories/story_001/

# Upload to YouTube with scheduling
python scripts/publisher.py --upload --story story_001 --schedule "2024-01-01 20:00"

# Batch upload multiple videos
python scripts/publisher.py --batch-upload ~/Claude/YouTube-Content/horror-stories/ready_for_upload/
```

### Testing and Development
```bash
# Run full pipeline test with sample story
python -m pytest tests/ -v

# Test individual phase
python -m pytest tests/test_story_processor.py::test_inspiration_integration -v

# Validate complete pipeline end-to-end
python scripts/pipeline_validator.py --test-story sample_horror_story
```

## External Tool Integration

### yt-dlp (YouTube Content Analysis)
- **Purpose**: Extract transcripts and metadata from successful horror channels
- **Installation**: `pip install yt-dlp`
- **Usage**: Transcript-only extraction (no video download) for story pattern analysis
- **Integration**: Subprocess calls from content_analyzer.py

### Fabric AI (Content Pattern Analysis)
- **Purpose**: Analyze transcripts for story structures, hooks, pacing patterns
- **Location**: Connected to local Ollama models  
- **Patterns**: Custom patterns for horror story analysis (extract_story_hooks, analyze_pacing_structure)
- **Integration**: Direct API calls for transcript processing

### Kokoro-FastAPI (Text-to-Speech)
- **Endpoint**: `http://localhost:8880/v1/audio/speech`
- **Docker**: `docker run -d -p 8880:8880 --name kokoro-full ghcr.io/remsky/kokoro-fastapi-cpu:latest`
- **Features**: 67 voice models, voice mixing, multiple formats (MP3/WAV)
- **Integration**: REST API calls from asset_generator.py

### StableDiffusion-Local (Image Generation)  
- **Location**: `~/Claude/StableDiffusion-Local/`
- **Command**: `python generate.py "prompt" --cpu --seed X --width 512 --height 288`
- **Performance**: 45-second generation, horror-capable DreamShaper-8 model
- **Integration**: CLI subprocess calls with batch processing

## Architecture Overview

### Pipeline Design
**5-Phase Sequential Pipeline:**
1. **Transcript Analysis**: Extract transcripts from successful horror channels → story patterns via Fabric AI
2. **Story Creation**: Patterns + templates → structured scripts + image prompts  
3. **Asset Generation**: Scripts → narration audio + atmospheric images
4. **Video Assembly**: Assets → synchronized MP4 with transitions
5. **Publishing**: Videos → YouTube upload with metadata

### Key Design Decisions
- **Transcript-Driven Research**: Analyze proven YouTube horror stories (not full videos)
- **AI Pattern Extraction**: Use Fabric AI to identify hooks, pacing, horror elements
- **Performance Correlation**: Link story patterns to view counts and engagement
- **Modular Architecture**: Horror-focused initially, designed for genre expansion
- **Content Separation**: Code in project repo, content in `~/Claude/YouTube-Content/`
- **Manual Quality Gates**: Human approval at each phase before proceeding
- **CLI-First**: All operations scriptable for automation and batch processing

### Project Structure
```
~/Claude/YouTube-StoryVideo-Generator/     # Code repository
├── scripts/                              # Phase-specific pipeline scripts
│   ├── content_analyzer.py               # Phase 0: Channel analysis
│   ├── inspiration_generator.py          # Phase 0: Pattern extraction  
│   ├── story_processor.py                # Phase 1: Story creation
│   ├── asset_generator.py                # Phase 2: Audio/image generation
│   ├── video_assembler.py                # Phase 3: Video compilation
│   └── publisher.py                      # Phase 4: YouTube publishing
├── config/                               # Configuration files
│   ├── channels_to_analyze.json          # Target channels for research
│   ├── story_patterns.json               # Extracted successful patterns
│   └── horror_voice_profiles.json        # Voice/genre matching
├── templates/                            # Story and workflow templates
└── research/                             # Transcript analysis and patterns
    ├── transcripts/                      # Downloaded YouTube transcripts  
    ├── fabric_analysis/                  # AI-generated story patterns
    └── performance_correlation/          # Success metrics analysis

~/Claude/YouTube-Content/                 # Content directory (separate)
├── horror-stories/                       # Genre-specific content
│   ├── story_001/
│   │   ├── script.json                   # Story script with metadata
│   │   ├── assets/
│   │   │   ├── narration/               # Generated audio files
│   │   │   ├── images/                  # Generated images
│   │   │   └── background-audio/        # Ambient tracks
│   │   └── output/                      # Final videos
│   └── ready_for_upload/                # Completed videos awaiting upload
```

## Key Implementation Notes

### Transcript Analysis Integration
- yt-dlp extracts transcripts (no video download) from high-performing horror channels
- Fabric AI analyzes transcripts for story hooks, pacing structures, horror elements
- Performance correlation links story patterns to view counts and engagement metrics
- Templates generated from proven successful patterns for original content creation

### Asset Generation Flow
- Story processor breaks scripts into timed segments with image prompts
- Kokoro-FastAPI generates narration with consistent horror-appropriate voice
- StableDiffusion-Local creates atmospheric images with style consistency via seeds
- Background audio sourced or generated for horror ambiance

### Video Assembly Process
- ffmpeg-based pipeline synchronizes narration, images, and background audio
- Configurable transitions and image duration for pacing control
- YouTube-optimized output format (1080p MP4, proper audio encoding)
- Preview mode for timing validation before final render

### Quality Control Gates
- Manual approval required between phases
- Asset validation checks audio quality, image consistency, timing accuracy
- Preview capabilities for story scripts, individual assets, and final videos
- Error handling and retry mechanisms for failed generations