# CLAUDE.md - YouTube Horror Story Video Generator

This project creates long-form horror story videos for YouTube using automated content generation and manual creative control.

## Project Vision

### Goal
Create engaging 1-2+ hour horror story videos for YouTube that combine:
- **Narrated Stories**: Human-quality voice narration of horror stories
- **Atmospheric Visuals**: AI-generated images that fade through the story
- **Background Audio**: Ambient horror soundscapes
- **Professional Quality**: YouTube-ready content for audience engagement

### Production Schedule
- **Weekly Batch Production**: One dedicated day per week
- **Output Target**: 7 complete videos per batch session
- **Content Length**: 1-2+ hours per video (feature-length content)
- **Genre Focus**: Horror stories initially, expandable to other genres

### Creative Control Philosophy
- **Manual Trigger**: Human initiates and oversees each production batch
- **Quality Control**: Manual review and approval at each stage
- **Creative Input**: Human storytelling with AI-powered asset generation
- **Scalable Process**: Efficient workflow that maintains creative standards

## Current Toolkit Integration

### Available AI Tools
Our existing infrastructure provides all core capabilities:

#### 1. Text-to-Speech: Kokoro-FastAPI ✅ READY
- **Location**: http://localhost:8880 (Docker container)
- **Capabilities**: 67 voice models, multi-language support
- **Quality**: Professional-grade narration
- **Integration**: REST API for automated narration generation
- **Features**: Voice mixing, multiple output formats (MP3, WAV)

#### 2. Image Generation: StableDiffusion-Local ✅ READY
- **Model**: Lykon/dreamshaper-8 (horror-capable)
- **Performance**: 45-second generation per image
- **Quality**: Excellent atmospheric and horror imagery
- **Control**: 20+ CLI parameters, seed control for consistency
- **Integration**: Command-line batch processing ready

#### 3. Content Management: ObsidianKnowledgeBase ✅ READY
- **Purpose**: Story research, organization, template management
- **Features**: AI-powered content classification and tagging
- **Integration**: N8N workflow automation
- **Storage**: Git-synchronized vault for story assets

#### 4. Workflow Automation: N8N ✅ READY
- **Capabilities**: Batch processing orchestration
- **Integration**: API bridges to all local AI tools
- **Features**: Queue management, error handling, status tracking
- **Architecture**: Docker-based with localhost API connections

## Production Pipeline Architecture

### Phase 1: Story Preparation
**Input**: Story concepts, themes, requirements
**Process**: 
- Story writing/adaptation for audio format
- Chapter/scene breakdown for image generation
- Timing calculations for narration pacing
- Image prompt creation for each story segment

**Tools**: ObsidianKnowledgeBase (templates, organization)
**Output**: Structured story script with image prompts

### Phase 2: Asset Generation
**Input**: Story scripts and image prompts from Phase 1
**Process**:
- **Narration Generation**: Kokoro-FastAPI batch processing
- **Image Creation**: StableDiffusion-Local batch generation
- **Background Audio**: Source or generate ambient horror soundscapes
- **Quality Control**: Manual review and approval of all assets

**Tools**: Kokoro-FastAPI + StableDiffusion-Local + N8N orchestration
**Output**: Complete asset library (audio narration, images, background tracks)

### Phase 3: Video Assembly
**Input**: All generated assets from Phase 2
**Process**:
- Combine narration audio with background soundscapes
- Synchronize images with story pacing and narration timing
- Apply smooth transitions between images
- Generate final video file(s) in YouTube-optimized format

**Tools**: To be implemented (ffmpeg-based video processing)
**Output**: Final 1-2+ hour MP4 videos ready for upload

### Phase 4: Publishing Workflow
**Input**: Completed videos from Phase 3
**Process**:
- YouTube metadata generation (titles, descriptions, tags)
- Thumbnail creation using generated horror images
- Upload and scheduling for consistent release schedule
- Performance tracking and optimization

**Tools**: YouTube API integration (to be implemented)
**Output**: Published and scheduled YouTube content

## Technical Implementation Strategy

### System Requirements Met
- **Apple M1 8GB Compatible**: All current tools proven to work within memory limits
- **Fast Generation**: 45-second images + instant narration = efficient workflow  
- **Proven Reliability**: Existing toolkit has demonstrated stability
- **CLI-First Design**: Scriptable and automatable production pipeline

### Development Approach
1. **Modular Design**: Each phase as independent, testable component
2. **CLI Interface**: Follow StableDiffusion-Local pattern for consistency
3. **Integration Ready**: Leverage existing N8N workflows and API patterns
4. **Quality First**: Manual approval gates at each critical stage

### File Structure Plan
```
~/Claude/YouTube-StoryVideo-Generator/
├── CLAUDE.md                 # This documentation
├── scripts/                  # Production pipeline scripts
│   ├── story_processor.py    # Phase 1: Story preparation
│   ├── asset_generator.py    # Phase 2: Batch asset creation
│   ├── video_assembler.py    # Phase 3: Video compilation
│   └── publisher.py          # Phase 4: YouTube workflow
├── templates/                # Story and workflow templates
├── assets/                   # Generated content storage
│   ├── stories/             # Story scripts and metadata
│   ├── narration/           # Generated audio files
│   ├── images/              # Generated visual assets
│   └── videos/              # Final output videos
└── config/                  # Configuration and settings
```

## Integration Points with Existing Infrastructure

### Kokoro-FastAPI Integration
- **Endpoint**: `http://localhost:8880/v1/audio/speech`
- **Batch Processing**: Sequential API calls for story chapters
- **Voice Selection**: Consistent narrator voice across series
- **Quality Settings**: Optimized for long-form content

### StableDiffusion-Local Integration
- **Command Pattern**: `python generate.py "horror prompt" --cpu --seed X`
- **Batch Generation**: Automated prompt processing from story scripts
- **Style Consistency**: Seed management for visual coherence
- **Performance**: 45-second generation fits production timeline

### N8N Workflow Integration
- **Queue Management**: Handle large batch processing jobs
- **Error Handling**: Retry failed generations, progress tracking
- **API Orchestration**: Coordinate between all AI services
- **Status Dashboard**: Monitor production pipeline progress

## Future Expansion Opportunities

### Content Scaling
- **Multiple Genres**: Mystery, sci-fi, fantasy, true crime
- **Series Creation**: Multi-part stories with character continuity
- **Interactive Elements**: Choose-your-own-adventure style content
- **Multi-Language**: Leverage Kokoro's language capabilities

### Technical Enhancements
- **Advanced Video Effects**: Transitions, animations, visual effects
- **Music Integration**: AI-generated background music creation
- **Voice Acting**: Multiple character voices in single stories
- **Live Streaming**: Real-time story generation and broadcast

### Business Integration
- **Analytics Dashboard**: Performance tracking and optimization
- **Content Management**: Story database and reuse capabilities
- **Audience Feedback**: Community-driven story selection
- **Monetization**: Optimized content for YouTube revenue

## Success Metrics

### Production Efficiency
- **Target**: 7 videos (1-2 hours each) per weekly batch day
- **Quality**: Professional-grade audio/visual consistency
- **Reliability**: Minimal manual intervention in asset generation
- **Scalability**: Ability to increase output without proportional time increase

### Content Quality
- **Audience Retention**: Long-form content engagement metrics
- **Visual Coherence**: Smooth image transitions and story synchronization
- **Audio Quality**: Clear narration with appropriate background mixing
- **Story Impact**: Engaging horror narratives that maintain viewer interest

## Getting Started

This project is designed for implementation in phases, allowing for iterative development and testing:

1. **Phase 1 Implementation**: Start with story processing and template creation
2. **Phase 2 Implementation**: Integrate existing AI tools for asset generation
3. **Phase 3 Implementation**: Develop video assembly pipeline
4. **Phase 4 Implementation**: Add YouTube publishing automation

Each phase can be developed and tested independently, with manual processes filling gaps until full automation is achieved.

---

**Status**: Planning Complete - Ready for Implementation
**Next Session Focus**: Begin Phase 1 development with story processing pipeline
**Key Dependencies**: All required AI tools already operational and tested