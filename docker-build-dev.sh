#!/usr/bin/env bash

# Build script for AllTalk development image
# Usage: ./docker-build-dev.sh

set -e

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $SCRIPT_DIR

echo "Building AllTalk development image..."
echo "This will:"
echo "  - Use existing base image (erew123/alltalk_tts_environment:latest)"
echo "  - Install Gradio 6.0+ for refactored code"
echo "  - Include development tools (ipdb, pytest, etc.)"
echo "  - Mount code as volume for live editing"
echo ""

# Build development image
docker build -f Dockerfile.dev \
  --build-arg DOCKER_REPOSITORY=erew123/ \
  --build-arg DOCKER_TAG=latest \
  --build-arg TTS_MODEL=xtts \
  --progress=plain \
  -t alltalk_tts:dev \
  .

if [ $? -eq 0 ]; then
  echo ""
  echo "✓ Development image built successfully!"
  echo ""
  echo "To run:"
  echo "  docker-compose -f docker-compose.dev.yml up -d"
  echo ""
  echo "To view logs:"
  echo "  docker-compose -f docker-compose.dev.yml logs -f"
  echo ""
  echo "To debug:"
  echo "  docker exec -it alltalk-dev bash"
  echo "  conda activate alltalk"
  echo "  python -m ipdb tts_server.py"
else
  echo ""
  echo "✗ Build failed!"
  exit 1
fi
