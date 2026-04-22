# 📥 Model Download System - Option D (Hybrid Approach)

## Overview

AllTalk TTS now supports **on-demand model downloads** to keep Docker images small (~2-4GB instead of 16GB+). Models are downloaded only when needed using one of three methods.

## 🎯 Why This Approach?

- **Smaller Docker Images**: Base image without models is only ~2-4GB
- **Faster Deployment**: Pull and start containers in minutes, not hours
- **Flexible**: Download only the models you need
- **Persistent**: Models stored in volumes survive container restarts
- **Easy Updates**: Update code without re-downloading models

## 📋 Three Ways to Download Models

### 1. 🖥️ Gradio UI (User-Friendly)

1. Start the container
2. Open Gradio UI at `http://localhost:7856`
3. Navigate to **"Model Downloads"** tab
4. Select your desired TTS engine
5. Click **"Download Model"**
6. Wait for download to complete

**Best for**: Interactive users, first-time setup

### 2. 💻 CLI Script (Developer-Friendly)

```bash
# From host machine
cd /path/to/alltalk_tts
python download_model.py --model xtts

# From inside Docker container
docker exec alltalk-dev python download_model.py --model xtts

# Check if model exists
python download_model.py --model xtts --check

# List available models
python download_model.py --model piper --list

# Force re-download
python download_model.py --model vits --force
```

**Best for**: Automation, scripts, CI/CD pipelines

### 3. 🔧 Environment Variables (Automated)

Set these in your `docker-compose.yml` or `.env` file:

```yaml
environment:
  - ALLTALK_AUTO_DOWNLOAD_MODEL=true
  - ALLTALK_DEFAULT_MODEL=xtts
  - TTS_MODEL=xtts
```

Or use the `--tts_model` argument in `firstrun.py`:

```bash
python ./system/config/firstrun.py --tts_model xtts
```

**Best for**: Automated deployments, production environments

## 🗂️ Available Models

| Engine | Size | Description |
|--------|------|-------------|
| **xtts** | ~1.8GB | High-quality multilingual TTS with voice cloning |
| **piper** | ~50MB | Fast, lightweight TTS (multiple language packs) |
| **vits** | ~100MB | Quality TTS with multiple voices |
| **f5tts** | ~500MB | F5-TTS model |
| **parler** | ~1GB | Parler TTS model |

## 📁 Model Storage

Models are stored in persistent volumes:

```
/home/alltalk/models/
├── xtts/
├── piper/
├── vits/
├── f5-tts/
└── rvc_voices/
```

These directories are mounted as Docker volumes and persist across container restarts.

## 🚀 Quick Start Examples

### Example 1: Start with XTTS (Auto-download)

```bash
# Set environment variables
export ALLTALK_AUTO_DOWNLOAD_MODEL=true
export ALLTALK_DEFAULT_MODEL=xtts

# Start container
docker compose -f docker-compose.dev.yml up -d

# XTTS model will download automatically on first run
```

### Example 2: Start without models (Manual download later)

```bash
# Default behavior - no auto-download
docker compose -f docker-compose.dev.yml up -d

# Download model via CLI when ready
docker exec alltalk-dev python download_model.py --model piper
```

### Example 3: Download multiple models

```bash
# Download XTTS
docker exec alltalk-dev python download_model.py --model xtts

# Download Piper
docker exec alltalk-dev python download_model.py --model piper

# Download VITS
docker exec alltalk-dev python download_model.py --model vits
```

## 🔍 Checking Model Status

```bash
# Check if XTTS is downloaded
docker exec alltalk-dev python download_model.py --model xtts --check

# List available Piper models
docker exec alltalk-dev python download_model.py --model piper --list
```

## ⚙️ Configuration

### Docker Compose Environment Variables

```yaml
services:
  alltalk-dev:
    environment:
      # Model download configuration
      - ALLTALK_AUTO_DOWNLOAD_MODEL=false  # Set to 'true' to enable auto-download
      - ALLTALK_DEFAULT_MODEL=none         # Options: xtts, piper, vits, none
      - TTS_MODEL=xtts                     # Model to use (for firstrun.py)
```

### Default Behavior

- **ALLTALK_AUTO_DOWNLOAD_MODEL**: `false` (no auto-download)
- **ALLTALK_DEFAULT_MODEL**: `none` (no default model)
- **TTS_MODEL**: `xtts` (used by firstrun.py if triggered)

## 🐛 Troubleshooting

### Model download fails

```bash
# Check logs
docker compose -f docker-compose.dev.yml logs --tail=100

# Try manual download with force flag
docker exec alltalk-dev python download_model.py --model xtts --force
```

### Gradio UI not showing Model Downloads tab

- Ensure you're using the latest code
- Check that `system/model_download_ui.py` exists
- Restart the container

### Models not persisting

- Check that volumes are correctly mounted in `docker-compose.yml`
- Verify the models directory exists: `docker exec alltalk-dev ls -la /home/alltalk/models`

## 📊 Disk Space Comparison

| Approach | Docker Image | Models | Total |
|----------|--------------|--------|-------|
| **Old (All Models)** | 16GB+ | Included | 16GB+ |
| **New (On-Demand)** | 2-4GB | 0-5GB | 2-9GB |

**Savings**: ~7-14GB depending on which models you download

## 🔄 Migration from Old System

If you're upgrading from the old system with pre-installed models:

1. Your existing models in volumes will still work
2. No need to re-download if models already exist
3. New models can be added using any of the three methods above

## 📝 Notes

- Models are downloaded from official sources
- Download times vary based on internet speed
- Some engines may require additional configuration
- Models can be shared across multiple containers using the same volume

## 🆘 Support

For issues or questions:
- Check the [AllTalk Wiki](https://github.com/erew123/alltalk_tts/wiki)
- Review [Error Messages List](https://github.com/erew123/alltalk_tts/wiki/Error-Messages-List)
- Open an issue on GitHub

---

**Last Updated**: April 22, 2026
**Version**: AllTalk v2.1 (Development)
