#!/usr/bin/env bash

# Build script for AllTalk production image
# Usage: ./docker-build-prod.sh

set -e

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $SCRIPT_DIR

TTS_MODEL=${1:-xtts}
TAG=${2:-latest}

echo "Building AllTalk production image..."
echo "  TTS Model: $TTS_MODEL"
echo "  Tag: $TAG"
echo ""
echo "This will:"
echo "  - Build minimal base environment from scratch"
echo "  - Install only required dependencies"
echo "  - Create optimized production image"
echo "  - Smaller download size (~3-4GB vs 8-10GB)"
echo ""

# Build production image
docker build -f Dockerfile.prod \
  --build-arg TTS_MODEL=$TTS_MODEL \
  --progress=plain \
  -t alltalk_tts:$TAG \
  .

if [ $? -eq 0 ]; then
  echo ""
  echo "✓ Production image built successfully!"
  echo ""
  echo "Image size:"
  docker images alltalk_tts:$TAG --format "{{.Size}}"
  echo ""
  echo "To run:"
  echo "  docker run -d --name alltalk \\"
  echo "    -p 7851:7851 -p 7852:7852 \\"
  echo "    --gpus all \\"
  echo "    alltalk_tts:$TAG"
else
  echo ""
  echo "✗ Build failed!"
  exit 1
fi
