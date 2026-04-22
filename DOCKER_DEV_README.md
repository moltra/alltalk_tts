# AllTalk Docker Development Guide

This guide covers building and running AllTalk in Docker for development and production.

## Quick Start (Development)

```bash
# SSH into Ubuntu machine
ssh your-user@192.168.0.116
cd /mnt/samsungssd/docker/appdata/alltalk/alltalk_test

# Build development image
chmod +x docker-build-dev.sh
./docker-build-dev.sh

# Run with docker-compose
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Access
# - Gradio UI: http://192.168.0.116:7852
# - API: http://192.168.0.116:7851
```

## Development vs Production Images

### Development Image (`Dockerfile.dev`)
**Purpose:** Fast iteration, debugging, testing refactored code

**Features:**
- ✓ Code mounted as volume (changes reflect instantly)
- ✓ Gradio 6.0+ (compatible with refactored code)
- ✓ Development tools (ipdb, ipython, pytest)
- ✓ Hot reload support
- ✓ All dependencies pre-installed
- ✗ Larger size (~8-10GB)

**Use when:**
- Developing new features
- Debugging issues
- Testing refactored code
- Running unit tests

### Production Image (`Dockerfile.prod`)
**Purpose:** Minimal footprint, optimized for deployment

**Features:**
- ✓ Multi-stage build (smaller layers)
- ✓ Only essential dependencies
- ✓ Optimized for size (~3-4GB)
- ✓ Security hardened
- ✗ No dev tools
- ✗ Code baked into image

**Use when:**
- Deploying to production
- Distributing to others
- Minimizing download size
- Running in resource-constrained environments

## Building Images

### Development Image

```bash
# Quick build (uses existing base image)
./docker-build-dev.sh

# Or with docker-compose
docker-compose -f docker-compose.dev.yml build
```

**Build time:** ~5-10 minutes
**Image size:** ~8-10GB
**Base:** `erew123/alltalk_tts_environment:latest`

### Production Image

```bash
# Build production image
chmod +x docker-build-prod.sh
./docker-build-prod.sh

# Build with specific model
./docker-build-prod.sh xtts prod-v1
```

**Build time:** ~30-40 minutes
**Image size:** ~3-4GB
**Base:** Built from scratch

## Running Containers

### Development (with docker-compose)

```bash
# Start
docker-compose -f docker-compose.dev.yml up -d

# Stop
docker-compose -f docker-compose.dev.yml down

# Restart
docker-compose -f docker-compose.dev.yml restart

# View logs
docker-compose -f docker-compose.dev.yml logs -f
```

### Production (with docker run)

```bash
docker run -d \
  --name alltalk \
  -p 7851:7851 \
  -p 7852:7852 \
  --gpus all \
  -v $(pwd)/models:/home/alltalk/models \
  -v $(pwd)/outputs:/home/alltalk/outputs \
  alltalk_tts:latest
```

## Debugging

### Enter Development Container

```bash
docker exec -it alltalk-dev bash
conda activate alltalk
cd /home/alltalk
```

### Run with Debugger

```bash
# Inside container
python -m ipdb tts_server.py

# Set breakpoints
# (Pdb) b tts_server.py:100
# (Pdb) c
```

### Run Tests

```bash
# Inside container
pytest
pytest -v tests/
pytest --cov=. tests/
```

### View Logs

```bash
# Real-time logs
docker logs -f alltalk-dev

# Last 100 lines
docker logs --tail 100 alltalk-dev

# With timestamps
docker logs -t alltalk-dev
```

## Development Workflow

1. **Make code changes** on Windows or Ubuntu
2. **Changes auto-sync** via volume mount
3. **Restart container** to apply changes
   ```bash
   docker-compose -f docker-compose.dev.yml restart
   ```
4. **View logs** to verify changes
5. **Commit and push** when ready

## Troubleshooting

### Container won't start

```bash
# Check logs
docker logs alltalk-dev

# Check if ports are in use
sudo netstat -tulpn | grep 7851
sudo netstat -tulpn | grep 7852

# Remove and recreate
docker-compose -f docker-compose.dev.yml down
docker-compose -f docker-compose.dev.yml up -d
```

### GPU not detected

```bash
# Verify nvidia-docker
docker run --rm --gpus all nvidia/cuda:12.8.1-base-ubuntu22.04 nvidia-smi

# Check container GPU access
docker exec -it alltalk-dev nvidia-smi
```

### Code changes not reflecting

```bash
# Verify volume mount
docker inspect alltalk-dev | grep Mounts -A 20

# Restart container
docker-compose -f docker-compose.dev.yml restart
```

### Permission issues

```bash
# Fix ownership
sudo chown -R $USER:$USER /mnt/samsungssd/docker/appdata/alltalk/alltalk_test

# Or run as root (not recommended)
docker exec -it -u root alltalk-dev bash
```

## File Structure

```
alltalk_tts/
├── Dockerfile              # Original production Dockerfile
├── Dockerfile.dev          # Development Dockerfile (new)
├── Dockerfile.prod         # Optimized production Dockerfile (new)
├── docker-compose.dev.yml  # Development compose file (new)
├── docker-build-dev.sh     # Development build script (new)
├── docker-build-prod.sh    # Production build script (new)
├── docker-build.sh         # Original build script
├── docker-start.sh         # Original start script
└── docker/
    ├── base/
    │   └── Dockerfile      # Base environment
    └── deepspeed/
        └── Dockerfile      # DeepSpeed build
```

## Next Steps

1. **Build development image** - Start here for refactoring work
2. **Test refactored code** - Verify Gradio 6.0 compatibility
3. **Run unit tests** - Ensure nothing broke
4. **Build production image** - When ready to deploy
5. **Push to registry** - Share with others

## Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/)
- [AllTalk GitHub](https://github.com/erew123/alltalk_tts)
