#!/usr/bin/env bash

# Convenience script to initialize config and start AllTalk dev container
# Usage: ./docker-start-dev.sh

set -e

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd "$SCRIPT_DIR"

echo "Starting AllTalk Development Environment"
echo ""

# Step 1: Initialize configuration
echo "Step 1: Initializing configuration..."
./docker-init-config.sh

# Step 2: Start Docker containers
echo ""
echo "Step 2: Starting Docker containers..."
docker compose -f docker-compose.dev.yml up -d

# Step 3: Show status
echo ""
echo "======================================"
echo "✓ AllTalk is starting!"
echo "======================================"
echo ""
echo "Access points:"
echo "  - API:        http://localhost:7851"
echo "  - Gradio UI:  http://localhost:7852"
echo ""
echo "Useful commands:"
echo "  View logs:    docker compose -f docker-compose.dev.yml logs -f"
echo "  Stop:         docker compose -f docker-compose.dev.yml down"
echo "  Restart:      docker compose -f docker-compose.dev.yml restart"
echo "  Shell access: docker exec -it alltalk-dev bash"
echo ""
