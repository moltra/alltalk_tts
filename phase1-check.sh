#!/usr/bin/env bash

# Phase 1: Development Docker Setup - Automated Checks
# Run this on Ubuntu machine after SSH

set -e

echo "=========================================="
echo "Phase 1: Development Docker Setup"
echo "=========================================="
echo ""

echo "1.2 Checking Docker installation..."
docker --version
docker-compose --version
echo "✓ Docker installed"
echo ""

echo "1.3 Checking NVIDIA Docker..."
docker run --rm --gpus all nvidia/cuda:12.8.1-base-ubuntu22.04 nvidia-smi
echo "✓ NVIDIA Docker working"
echo ""

echo "1.4 Checking disk space..."
df -h /mnt/samsungssd | grep -v Filesystem
AVAILABLE=$(df -h /mnt/samsungssd | grep -v Filesystem | awk '{print $4}')
echo "Available: $AVAILABLE"
echo "Required: 20GB+"
echo ""

echo "1.5 Navigating to project directory..."
cd /mnt/samsungssd/docker/appdata/alltalk/alltalk_test
pwd
echo "✓ In project directory"
echo ""

echo "1.6 Syncing refactored code..."
git pull origin V2.1
echo "✓ Code synced"
echo ""

echo "1.7 Verifying refactored files..."
ls -la system/exceptions.py
ls -la system/error_handler.py
ls -la system/logging_config.py
echo "✓ Refactored files present"
echo ""

echo "1.8 Verifying Docker files..."
ls -la Dockerfile.dev
ls -la docker-compose.dev.yml
ls -la docker-build-dev.sh
echo "✓ Docker files present"
echo ""

echo "=========================================="
echo "✓ Phase 1 Complete!"
echo "=========================================="
echo ""
echo "Ready to proceed to Phase 2: Build"
echo "Run: ./docker-build-dev.sh"
