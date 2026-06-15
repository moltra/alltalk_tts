# AllTalk Docker Quick Start Guide

## Development Environment

### Option 1: One-Command Start (Recommended)

```bash
./docker-start-dev.sh
```

This script will:
1. Initialize configuration files
2. Create required directories
3. Start the Docker containers
4. Display access URLs

### Option 2: Manual Steps

```bash
# Step 1: Initialize configuration (IMPORTANT - prevents config file issues)
./docker-init-config.sh

# Step 2: Start containers
docker compose -f docker-compose.dev.yml up -d

# Step 3: View logs
docker compose -f docker-compose.dev.yml logs -f
```

### Access Points

- **API**: http://localhost:7851
- **Gradio UI**: http://localhost:7852

### Common Commands

```bash
# View logs
docker compose -f docker-compose.dev.yml logs -f

# Stop containers
docker compose -f docker-compose.dev.yml down

# Restart containers
docker compose -f docker-compose.dev.yml restart

# Access container shell
docker exec -it alltalk-dev bash

# Rebuild after code changes (if needed)
./docker-build-dev.sh
docker compose -f docker-compose.dev.yml up -d
```

## Production Environment

### Build and Run

```bash
# Build production image
./docker-build-prod.sh

# Run container
docker run -d --name alltalk \
  -p 7851:7851 -p 7852:7852 \
  --gpus all \
  alltalk_tts:latest
```

### Access Points

- **API**: http://localhost:7851
- **Gradio UI**: http://localhost:7852

## Important Notes

### Configuration Files

⚠️ **Always run `./docker-init-config.sh` before first start!**

This prevents Docker from creating config files as directories, which causes startup failures.

The script:
- Creates `/mnt/samsungssd/docker/appdata/alltalk/alltalk_test/confignew.json`
- Creates required directories (models, outputs, voices)
- Validates existing config files

### Custom Configuration Directory

To use a different config directory:

```bash
export HOST_CONFIG_DIR=/path/to/your/config
./docker-init-config.sh
```

Then update the volume mount in `docker-compose.dev.yml` accordingly.

**Note**: This guide uses `docker compose` (Docker Compose V2). If you have the older version installed, use `docker-compose` (with hyphen) instead.

### Development Workflow

1. **Code changes** in `system/`, `config/`, `tts_server.py`, etc. are **immediately reflected** (no rebuild needed)
2. **Dockerfile changes** require rebuild: `./docker-build-dev.sh`
3. **Dependency changes** require rebuild: `./docker-build-dev.sh`

### Troubleshooting

**Problem**: Config file is a directory
```bash
# Solution: Remove and recreate
rm -rf /mnt/samsungssd/docker/appdata/alltalk/alltalk_test/confignew.json
./docker-init-config.sh
```

**Problem**: Container won't start
```bash
# Check logs
docker compose -f docker-compose.dev.yml logs

# Or for production
docker logs alltalk
```

**Problem**: GPU not detected
```bash
# Verify GPU is available to Docker
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi
```

**Problem**: Port already in use
```bash
# Find what's using the port
sudo lsof -i :7855
sudo lsof -i :7856

# Or change ports in docker-compose.dev.yml
```

## File Structure

```
alltalk_tts/
├── docker-init-config.sh       # Initialize config files (run first!)
├── docker-start-dev.sh         # Convenience script (recommended)
├── docker-build-dev.sh         # Build dev image
├── docker-build-prod.sh        # Build prod image
├── docker-compose.dev.yml      # Dev environment config
├── Dockerfile.dev              # Dev Dockerfile
├── Dockerfile.prod             # Prod Dockerfile
└── config/
    └── app/
        └── confignew.json      # Template config file
```

## Next Steps

After starting AllTalk:

1. Open Gradio UI: http://localhost:7856
2. Select a TTS model in the settings
3. Generate your first TTS audio!

For API usage, see the API documentation at http://localhost:7856 (Documentation tab).
