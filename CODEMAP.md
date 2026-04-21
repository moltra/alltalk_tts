# AllTalk TTS v2 - Code Map

## Project Overview
AllTalk TTS v2 is a comprehensive Text-to-Speech framework with multiple TTS engine support, voice conversion capabilities, web interface, and API integration.

**Repository:** https://github.com/erew123/alltalk_tts
**Language:** Python
**Primary Frameworks:** FastAPI, Gradio, PyTorch

---

## Root-Level Files

### Core Application Files
- **`tts_server.py`** (2,620 lines) - Main FastAPI server implementation
  - API endpoints for TTS generation, model management, voice conversion
  - Handles RVC (Retrieval-based Voice Conversion) pipeline
  - OpenAI-compatible API endpoints
  - Configuration reload and model switching
  - Audio file serving with caching

- **`script.py`** (4,965 lines) - Gradio web interface and main application logic
  - WebUI for TTS generation and management
  - Integration with Text-Generation-WebUI (TGWUI)
  - Transcription utilities using Whisper
  - Audio file processing and validation
  - Bulk TTS generator/editor
  - First-time setup and configuration

- **`config.py`** (414 lines) - Configuration management system
  - Pydantic-based configuration models
  - Singleton pattern for config instances
  - File locking and backup for config changes
  - Hot-reload capabilities
  - Multiple config classes for different components

- **`finetune.py`** (4,810 lines) - XTTS model fine-tuning module
  - Dataset creation and preprocessing
  - Model training with custom trainer
  - Gradio interface for fine-tuning
  - Audio sample processing
  - Training metrics logging

- **`tts_mem.py`** (1,517 lines) - Multi-Engine Manager (MEM) - Experimental
  - Manages multiple TTS engine instances simultaneously
  - Request queueing and load balancing
  - Flask-based API for MEM management
  - Process monitoring and health checks
  - Gradio interface for MEM control

- **`diagnostics.py`** (51,784 lines) - System diagnostics tool
  - Environment validation
  - Dependency checking
  - Configuration verification
  - Automated repair capabilities

### Setup and Installation
- **`atsetup.bat`** (32,441 bytes) - Windows setup script
- **`atsetup.sh`** (19,352 bytes) - Linux/macOS setup script
- **`Dockerfile`** (8,516 bytes) - Docker container configuration
- **`docker-build.sh`** - Docker build script
- **`docker-start.sh`** - Docker startup script

### Configuration Files
- **`confignew.json`** - Main application configuration
- **`mem_config.json`** - Multi-Engine Manager configuration
- **`docker_confignew.json`** - Docker-specific configuration
- **`docker_default_confignew.json`** - Docker default configuration
- **`docker_default_mem_config.json`** - Docker MEM configuration

### Documentation
- **`README.md`** - Main project documentation
- **`DOCKER_README.md`** - Docker-specific documentation
- **`LICENSE`** - Project license

### Testing
- **`test_server.py`** (51,894 bytes) - Server testing utilities
- **`test/`** - Test configuration files
  - `test_config.py` - Configuration testing
  - `confignew_partial.json` - Partial config for testing
  - `empty.json` - Empty config for testing

### Notebooks
- **`googlecolab.ipynb`** - Google Colab notebook for cloud deployment

---

## System Directory Structure

### `system/config/`
Configuration and first-run setup
- **`firstrun.py`** - First-time setup wizard
- **`firstrun_tgwui.py`** - TGWUI-specific first-run setup
- **`languages.json`** - Supported languages mapping
- **`harvard_sentences.txt`** - Test sentences for TTS
- **`basediagnostics.log`** - Baseline diagnostics reference
- **`fixsymlinks.sh`** - Symlink repair script
- **`symlinks_cuda_toolkit_breaks.txt`** - Known CUDA symlink issues
- **`fairseq-*.whl`** - Fairseq wheel files for different platforms

### `system/requirements/`
Dependency specifications for different environments
- **`requirements_standalone.txt`** - Standalone deployment
- **`requirements_textgen.txt`** - Text-Generation-WebUI integration
- **`requirements_textgen2.txt`** - TGWUI alternative
- **`requirements_colab.txt`** - Google Colab environment
- **`requirements_f5tts.txt`** - F5 TTS engine dependencies
- **`requirements_parler.txt`** - Parler TTS engine dependencies
- **`requirements_unit_test.txt`** - Unit testing dependencies

### `system/tts_engines/`
TTS engine implementations and configurations

#### Engine Directories
- **`xtts/`** - Coqui XTTS TTS engine
  - `model_engine.py` - Engine implementation
  - `available_models.json` - Model registry
  - `model_settings.json` - Engine settings
  - Help content and settings pages

- **`vits/`** - Coqui VITS TTS engine
  - Similar structure to XTTS

- **`piper/`** - Piper TTS engine
  - `model_engine.py` - Engine implementation
  - `piper_settings_page.py` - Gradio settings
  - `piper_gitclone_scanner.py` - Model scanner
  - `engine/` - Piper engine code (368 items)

- **`parler/`** - Parler TTS engine
  - `model_engine.py` - Engine implementation
  - `parler_settings_page.py` - Gradio settings
  - Help content and model configs

- **`f5tts/`** - F5 TTS engine
  - `model_engine.py` - Engine implementation
  - `f5tts_settings_page.py` - Gradio settings
  - Help content and model configs

- **`rvc/`** - Retrieval-based Voice Conversion
  - `infer/infer.py` - RVC inference pipeline
  - `infer/pipeline.py` - Pipeline implementation
  - `lib/` - RVC library modules
    - `FCPEF0Predictor.py` - F0 pitch prediction
    - `rmvpe.py` - RMVPE pitch extraction
    - `infer_pack/` - Neural network modules
      - `models.py` - Model architectures
      - `modules/` - F0 predictors (Dio, Harvest, PM, FCPE)
      - `attentions.py` - Attention mechanisms
      - `commons.py` - Common utilities
      - `transforms.py` - Audio transforms
    - `tools/` - Utility tools
      - `analyzer.py` - Audio analysis
      - `gdown.py` - Google Drive downloader
  - `configs/` - RVC configuration files
    - `v1/` - Version 1 configs (32k, 40k, 48k)
    - `v2/` - Version 2 configs (32k, 48k)

- **`template-tts-engine/`** - Template for adding new engines
  - Reference implementation for new TTS engines

#### Engine Configuration Files
- **`tts_engines.json`** - Available engines registry
- **`new_engines.json`** - New engine additions
- **`rvc_files.json`** - RVC file registry

### `system/gradio_pages/`
Gradio web interface components
- **`help_content.py`** - Help documentation content
- **`alltalk_diskspace.py`** - Disk space monitoring
- **`themes/`** - Gradio theme management
  - `themes.py` - Theme definitions
  - `loadThemes.py` - Theme loader
  - `theme_list.json` - Available themes

### `system/tts_generator/`
TTS generation utilities
- Audio processing modules
- Text preprocessing
- Output formatting

### `system/tts_srt/`
Subtitle generation from TTS
- **`tts_srt.py`** - SRT file generation

### `system/tts_diff/`
TTS comparison tools
- **`tts_diff.py`** - Audio comparison utilities

### `system/proxy_module/`
Reverse proxy functionality
- **`proxy_manager.py`** - Proxy management
- **`twisted_server.py`** - Twisted-based server
- **`interface.py` - Proxy interface
- **`cert_maker.py`** - Certificate generation
- **`cert_manager.py`** - Certificate management
- **`health_monitor.py`** - Health monitoring
- **`metrics.py`** - Metrics collection
- **`security.py`** - Security utilities

### `system/ft_tokenizer/`
Fine-tuning tokenizer utilities
- **`tokenizer.py`** - Tokenizer implementation
- **`custom_tokenizer.py`** - Custom tokenizer
- **`expand_xtts.py`** - XTTS expansion
- **`extract_dataset_for_tokenizer.py`** - Dataset extraction
- **`compare_and_merge.py` - Token comparison

### `system/espeak-ng/`
eSpeak-ng phoneme support
- Phoneme conversion utilities

### `system/win_ffmpeg/`
Windows FFmpeg distribution
- FFmpeg binaries for Windows

### `system/word_addin/`
Microsoft Word add-in
- Word integration for TTS (14 items)

### `system/cliptotts/`
Clipboard to TTS utility
- **`clipboard-to-tts.py`** - Clipboard monitoring and TTS

### `system/at_admin/`
Administration tools
- Admin utilities

### `system/SillyTavern_Extension/`
SillyTavern integration
- Extension files for SillyTavern (4 items)

### `system/TGWUI_Extension/`
Text-Generation-WebUI integration
- **`script.py`** - TGWUI integration script
- **`languages.json`** - Language mappings
- **`tgwui_remote_config.json`** - Remote configuration
- Extension files (9 items)

### Static Files
- **`admin.html`** (37,113 bytes) - Admin interface
- **`openaittstest.html`** (7,229 bytes) - OpenAI API test page
- **`favicon.ico`** - Web interface favicon

---

## Trainer Directory (`trainer_alltalk/`)
Custom training utilities for fine-tuning
- **`trainer.py`** - Custom trainer implementation
- **`metrics_logger.py`** - Training metrics logging
- **`finetune_content.py`** - Fine-tuning help content

---

## Key Architectural Patterns

### Configuration Management
- **Singleton Pattern**: All config classes use singleton pattern (`get_instance()`)
- **Pydantic Models**: Type-safe configuration with validation
- **Hot Reload**: Config files auto-reload on modification
- **File Locking**: Uses `filelock` for safe concurrent access
- **Backup System**: Automatic backup before config changes

### TTS Engine Architecture
- **Plugin System**: Each TTS engine is a self-contained module
- **Abstract Interface**: All engines implement common interface
- **Dynamic Loading**: Engines loaded dynamically via `importlib`
- **Model Swapping**: Runtime model and engine switching
- **Capability Flags**: Each engine advertises capabilities (deepspeed, lowvram, etc.)

### API Design
- **FastAPI**: RESTful API with async support
- **OpenAI Compatibility**: Drop-in replacement for OpenAI TTS API
- **Streaming Support**: Real-time audio streaming
- **CORS Enabled**: Cross-origin requests supported
- **Error Handling**: Comprehensive exception handling with logging

### Multi-Engine Manager (MEM)
- **Process Pool**: Manages multiple TTS server processes
- **Request Queue**: Queues requests across available instances
- **Load Balancing**: Distributes requests based on availability
- **Health Monitoring**: Monitors engine health and restarts if needed
- **Experimental**: Marked as experimental, not production-ready

---

## Data Flow

### TTS Generation Flow
1. Client request → API endpoint (`/api/tts` or OpenAI endpoint)
2. Text preprocessing (filtering, language detection)
3. Engine-specific model inference
4. Optional RVC voice conversion
5. Audio post-processing (transcoding, normalization)
6. File output or streaming response

### Configuration Reload Flow
1. Config file modification detected
2. File lock acquired
3. Backup created
4. New config loaded and validated
5. Model/engine reinitialization if needed
6. Lock released, backup cleaned up

### MEM Request Flow
1. Request received at MEM API
2. Queued if all instances busy
3. Assigned to available instance
4. Forwarded to instance's API
5. Response returned to client
6. Instance marked available

---

## Dependencies

### Core Dependencies
- **FastAPI/Uvicorn** - Web server
- **Gradio** - Web UI framework
- **PyTorch** - Deep learning framework
- **Pydantic** - Data validation
- **librosa/soundfile** - Audio processing
- **ffmpeg-python** - Audio transcoding

### TTS Engine Dependencies
- **TTS (Coqui)** - XTTS, VITS engines
- **Piper** - Piper TTS engine
- **Transformers** - Parler, F5 TTS engines

### Voice Conversion
- **torch** - PyTorch for RVC
- **fairseq** - Audio processing

### ASR/Transcription
- **openai-whisper** - Speech recognition
- **langdetect** - Language detection

### Utilities
- **tqdm** - Progress bars
- **requests** - HTTP client
- **aiofiles** - Async file operations
- **filelock** - File locking

---

## Integration Points

### External Integrations
- **Text-Generation-WebUI** - AI chat interface
- **SillyTavern** - Roleplay chat interface
- **KoboldCPP** - Text generation
- **HomeAssistant** - Home automation
- **Word Add-in** - Microsoft Word integration

### API Compatibility
- **OpenAI TTS API** - Compatible endpoint
- **JSON API** - Custom JSON format
- **REST API** - Standard REST endpoints

---

## Key Features

### TTS Capabilities
- Multi-engine support (XTTS, VITS, Piper, Parler, F5)
- Voice cloning and fine-tuning
- RVC voice conversion
- Multi-language support
- Custom voice samples
- Bulk generation

### Audio Processing
- Format transcoding (WAV, MP3, OPUS, etc.)
- Audio normalization
- Noise reduction
- Bandpass filtering
- Sample rate conversion

### Performance
- DeepSpeed integration (2-3x speedup)
- Low VRAM mode
- GPU acceleration (NVIDIA)
- CPU fallback
- Streaming support

### Management
- Model download manager
- Configuration hot-reload
- Process monitoring
- Health checks
- Diagnostics tool

### Experimental
- Multi-Engine Manager (MEM)
- Concurrent request handling
- Request queuing

---

## Security Considerations

### Current Security Features
- CORS configuration (currently allows all origins)
- Certificate management for proxy
- Input validation via Pydantic
- File locking for config

### Security Notes
- CORS set to allow all origins (`allow_origins=["*"]`)
- Portaudio optional dependency
- FFmpeg required for transcoding
- Config files contain sensitive settings

---

## Known Limitations

### Platform Support
- Mac support is theoretical/untested
- AMD GPU support is experimental (Linux only)
- Intel ARC GPUs not supported
- Apple Silicon no GPU acceleration

### Engine Limitations
- Some engines CPU-only (very slow)
- RVC requires specific model formats
- Fine-tuning requires significant resources
- MEM is experimental, not production-ready

---

## Development Notes

### Code Style
- Uses type hints in some areas
- Extensive debug logging system
- Global variables used in several places
- Mixed sync/async patterns

### Testing
- Limited test coverage
- Main testing in `test_server.py`
- Configuration tests in `test/`
- No unit test framework evident

### Documentation
- Comprehensive README
- Built-in help system
- GitHub Wiki
- Inline docstrings present but inconsistent

---

## File Size Summary

- **Large Files (>10KB):**
  - `diagnostics.py` - 51,784 bytes
  - `script.py` - 217,193 bytes (estimated from line count)
  - `tts_server.py` - 123,382 bytes (estimated)
  - `finetune.py` - 193,953 bytes (estimated)
  - `atsetup.bat` - 32,441 bytes
  - `admin.html` - 37,113 bytes

- **Medium Files (1-10KB):**
  - `config.py` - 16,603 bytes
  - `tts_mem.py` - 81,106 bytes (estimated)
  - `README.md` - 8,849 bytes
  - `Dockerfile` - 8,516 bytes

---

## Entry Points

### Main Entry Points
1. **`python script.py`** - Start Gradio web interface
2. **`python tts_server.py`** - Start FastAPI server only
3. **`python tts_mem.py`** - Start Multi-Engine Manager
4. **`python finetune.py`** - Start fine-tuning interface
5. **`python diagnostics.py`** - Run diagnostics tool

### Setup Entry Points
1. **`atsetup.bat`** (Windows) - Automated setup
2. **`bash atsetup.sh`** (Linux/macOS) - Automated setup
3. **Manual setup** - Per README instructions

---

## Configuration Hierarchy

1. **`confignew.json`** - Main application config
2. **`mem_config.json`** - MEM-specific config
3. **`system/tts_engines/tts_engines.json`** - Engine registry
4. **`system/tts_engines/new_engines.json`** - New engine additions
5. **`system/tts_engines/{engine}/model_settings.json`** - Engine-specific settings
6. **`system/tts_engines/{engine}/available_models.json`** - Model registry

---

## Output Directories

- **`outputs/`** - Generated audio files
- **`finetune/`** - Fine-tuning data and models
- **`models/`** - Downloaded TTS models
- **`voices/`** - Custom voice samples
- **`finetune/tmp-trn/`** - Temporary training data

---

## Logging and Debugging

### Debug Flags (in config.debugging)
- `debug_transcode` - Audio transcoding
- `debug_tts` - TTS generation
- `debug_openai` - OpenAI API
- `debug_concat` - Audio concatenation
- `debug_tts_variables` - TTS variable tracking
- `debug_rvc` - RVC processing
- `debug_func` - Function entry/exit
- `debug_api` - API calls
- `debug_fullttstext` - Full TTS text
- `debug_narrator` - Narrator function
- `debug_gradio_IP` - Gradio IP handling
- `debug_transcribe` - Transcription
- `debug_proxy` - Proxy operations

### Logging System
- Centralized `print_message()` function
- Color-coded output (blue, yellow, red, green)
- Component-based prefixes (TTS, ENG, API, GEN)
- Conditional debug output based on flags

---

## This Codemap

Generated on: 2025-04-21
Repository: https://github.com/erew123/alltalk_tts
Version: v2
Purpose: Code structure documentation and navigation guide
