# AllTalk Docker Deployment Plan

**Project:** AllTalk TTS V2.1 Refactored
**Goal:** Deploy refactored code in Docker for development and production
**Date Started:** April 21, 2026
**Status:** Phase 1 - Preparation

---

## Overview

### Objectives
- [x] Create development Docker image with debugging tools
- [x] Create production Docker image with minimal footprint
- [ ] Test refactored code in Docker environment
- [ ] Verify Gradio 6.0 compatibility
- [ ] Validate all refactoring improvements
- [ ] Deploy production-ready image

### Key Changes from Original
- **Gradio:** 4.32.2 → 6.0+ (refactored code requirement)
- **Code mounting:** Baked-in → Volume mount (dev only)
- **Dev tools:** None → ipdb, pytest, ipython
- **Image size:** 8-10GB → 3-4GB (production)
- **Ports:** 7851/7852 (internal) → 7855/7856 (external, dev)

---

## Phase 1: Development Docker Setup ⏳

**Status:** Not Started
**Estimated Time:** 15 minutes
**Prerequisites:** SSH access to Ubuntu, Docker installed

### Tasks

- [ ] **1.1 SSH into Ubuntu machine**
  ```bash
  ssh your-user@192.168.0.116
  ```

- [ ] **1.2 Verify Docker installation**
  ```bash
  docker --version
  docker-compose --version
  ```
  Expected: Docker 20.10+, docker-compose 1.29+

- [ ] **1.3 Verify NVIDIA Docker**
  ```bash
  docker run --rm --gpus all nvidia/cuda:12.8.1-base-ubuntu22.04 nvidia-smi
  ```
  Expected: GPU info displayed

- [ ] **1.4 Check disk space**
  ```bash
  df -h /mnt/samsungssd
  ```
  Required: 20GB+ free
  Actual: _________

- [ ] **1.5 Navigate to project directory**
  ```bash
  cd /mnt/samsungssd/docker/appdata/alltalk/alltalk_test
  pwd
  ```

- [ ] **1.6 Sync refactored code**
  ```bash
  git pull origin V2.1
  ```

- [ ] **1.7 Verify new refactored files exist**
  ```bash
  ls -la system/exceptions.py
  ls -la system/error_handler.py
  ls -la system/logging_config.py
  ```

- [ ] **1.8 Verify Docker files exist**
  ```bash
  ls -la Dockerfile.dev
  ls -la docker-compose.dev.yml
  ls -la docker-build-dev.sh
  ```

### Success Criteria
- ✓ SSH connection working
- ✓ Docker and NVIDIA Docker functional
- ✓ Sufficient disk space available
- ✓ Refactored code present
- ✓ Docker build files present

### Issues Encountered
_Document any problems here_

---

## Phase 2: Development Docker Build ⏳

**Status:** Not Started
**Estimated Time:** 5-10 minutes
**Dependencies:** Phase 1 complete

### Tasks

- [ ] **2.1 Make build script executable**
  ```bash
  chmod +x docker-build-dev.sh
  ```

- [ ] **2.2 Review build script**
  ```bash
  cat docker-build-dev.sh
  ```
  Verify: Uses erew123/alltalk_tts_environment:latest base

- [ ] **2.3 Start build**
  ```bash
  ./docker-build-dev.sh
  ```
  Start time: _________

- [ ] **2.4 Monitor build progress**
  Watch for:
  - Pulling base image
  - Installing Gradio 6.0+
  - Installing dev dependencies (ipdb, pytest)
  - Installing DeepSpeed
  - Creating startup scripts

- [ ] **2.5 Build completion**
  End time: _________
  Duration: _________
  Expected: "✓ Development image built successfully!"

- [ ] **2.6 Verify image created**
  ```bash
  docker images alltalk_tts:dev
  ```
  Expected size: 8-10GB
  Actual size: _________

- [ ] **2.7 Inspect image**
  ```bash
  docker inspect alltalk_tts:dev | grep -A 10 "Env"
  ```
  Verify: GRADIO_SERVER_NAME, ALLTALK_DIR set

### Success Criteria
- ✓ Build completes without errors
- ✓ Image size is reasonable (8-10GB)
- ✓ Environment variables set correctly

### Build Log
```
Paste build output here if issues occur
```

### Issues Encountered
_Document any problems here_

---

## Phase 3: Development Docker Test ⏳

**Status:** Not Started
**Estimated Time:** 10 minutes
**Dependencies:** Phase 2 complete

### Tasks

- [ ] **3.1 Start container with docker-compose**
  ```bash
  docker-compose -f docker-compose.dev.yml up -d
  ```

- [ ] **3.2 Watch startup logs**
  ```bash
  docker-compose -f docker-compose.dev.yml logs -f
  ```
  Watch for:
  - Conda environment activated
  - Dependencies loaded
  - Gradio server starting on 0.0.0.0:7852
  - API server starting on 0.0.0.0:7851
  - No errors

- [ ] **3.3 Verify container running**
  ```bash
  docker ps | grep alltalk-dev
  ```
  Expected: STATUS = Up

- [ ] **3.4 Check GPU access**
  ```bash
  docker exec -it alltalk-dev nvidia-smi
  ```
  Expected: GPU info displayed

- [ ] **3.5 Check conda environment**
  ```bash
  docker exec -it alltalk-dev bash -c "source conda_env.sh && conda info --envs"
  ```
  Expected: alltalk environment active

- [ ] **3.6 Test API from Ubuntu**
  ```bash
  curl http://localhost:7855/api/ready
  ```
  Expected: "Ready"

- [ ] **3.7 Test Gradio UI from Windows**
  Open browser: http://192.168.0.116:7856
  Expected: Gradio interface loads

- [ ] **3.8 Test API from Windows**
  Open browser: http://192.168.0.116:7855/api/ready
  Expected: "Ready"

- [ ] **3.9 Test volume mount**
  ```bash
  # On Ubuntu
  echo "# Test change" >> tts_server.py

  # Inside container
  docker exec -it alltalk-dev bash -c "tail -n 1 /home/alltalk/tts_server.py"

  # Revert
  git checkout tts_server.py
  ```
  Expected: Change visible in container

- [ ] **3.10 Test TTS generation**
  Use Gradio UI to generate test audio
  Expected: Audio file created in outputs/

### Success Criteria
- ✓ Container starts without errors
- ✓ GPU accessible
- ✓ API responds correctly
- ✓ Gradio UI loads
- ✓ Volume mounts working
- ✓ TTS generation works

### Test Results
| Test | Expected | Actual | Pass/Fail |
|------|----------|--------|-----------|
| Container starts | Up | | |
| GPU access | Yes | | |
| API ready | "Ready" | | |
| Gradio UI | Loads | | |
| Volume mount | Syncs | | |
| TTS generation | Audio created | | |

### Issues Encountered
_Document any problems here_

---

## Phase 4: Development Docker Debug ⏳

**Status:** Not Started
**Estimated Time:** 15 minutes
**Dependencies:** Phase 3 complete

### Tasks

- [ ] **4.1 Enter container interactively**
  ```bash
  docker exec -it alltalk-dev bash
  source conda_env.sh
  ```

- [ ] **4.2 Test Python debugger (ipdb)**
  ```bash
  python -m ipdb tts_server.py
  # (Pdb) b tts_server.py:50
  # (Pdb) c
  # (Pdb) quit
  ```
  Expected: Debugger starts, breakpoint works

- [ ] **4.3 Run unit tests**
  ```bash
  pytest
  ```
  Expected: Tests run, results displayed

- [ ] **4.4 Run tests with coverage**
  ```bash
  pytest --cov=. tests/
  ```
  Expected: Coverage report generated

- [ ] **4.5 Test specific module**
  ```bash
  pytest tests/test_config.py -v
  ```
  Expected: Config tests pass

- [ ] **4.6 View real-time logs**
  ```bash
  docker-compose -f docker-compose.dev.yml logs -f
  ```

- [ ] **4.7 Search logs for errors**
  ```bash
  docker logs alltalk-dev 2>&1 | grep ERROR
  ```
  Expected: No critical errors

- [ ] **4.8 Test hot reload workflow**
  ```bash
  # Edit file on host
  vim tts_server.py  # Add comment

  # Restart container
  docker-compose -f docker-compose.dev.yml restart

  # Verify change
  docker-compose -f docker-compose.dev.yml logs -f
  ```
  Expected: Change reflected after restart

- [ ] **4.9 Test Loguru logging**
  Check logs for Loguru formatted messages
  Expected: Structured logging visible

- [ ] **4.10 Verify error handling**
  Trigger an error, check exception handling
  Expected: Custom exceptions caught, logged properly

### Success Criteria
- ✓ Debugger works correctly
- ✓ Tests run successfully
- ✓ Logs are accessible and formatted
- ✓ Hot reload workflow functional
- ✓ Error handling works as expected

### Debug Session Notes
```
Document debugging findings here
```

### Issues Encountered
_Document any problems here_

---

## Phase 5: Production Docker Build ⏳

**Status:** Not Started (Do Later)
**Estimated Time:** 30-40 minutes
**Dependencies:** Phase 4 complete, refactoring validated

### Tasks

- [ ] **5.1 Make production build script executable**
  ```bash
  chmod +x docker-build-prod.sh
  ```

- [ ] **5.2 Review production Dockerfile**
  ```bash
  cat Dockerfile.prod
  ```
  Verify: Multi-stage build, minimal dependencies

- [ ] **5.3 Start production build**
  ```bash
  ./docker-build-prod.sh
  ```
  Start time: _________

- [ ] **5.4 Monitor build progress**
  Watch for:
  - Building base environment from scratch
  - Installing minimal dependencies
  - Optimizing layers
  - Final image creation

- [ ] **5.5 Build completion**
  End time: _________
  Duration: _________

- [ ] **5.6 Verify image size**
  ```bash
  docker images alltalk_tts:latest
  ```
  Expected: 3-4GB
  Actual: _________

- [ ] **5.7 Compare image sizes**
  ```bash
  docker images | grep alltalk_tts
  ```
  Dev vs Prod size difference: _________

### Success Criteria
- ✓ Build completes without errors
- ✓ Image size significantly smaller than dev (~3-4GB)
- ✓ All required dependencies included

### Issues Encountered
_Document any problems here_

---

## Phase 6: Production Docker Test ⏳

**Status:** Not Started (Do Later)
**Estimated Time:** 15 minutes
**Dependencies:** Phase 5 complete

### Tasks

- [ ] **6.1 Run production container**
  ```bash
  docker run -d \
    --name alltalk-prod \
    -p 7857:7851 \
    -p 7858:7852 \
    --gpus all \
    -v $(pwd)/models:/home/alltalk/models \
    -v $(pwd)/outputs:/home/alltalk/outputs \
    alltalk_tts:latest
  ```

- [ ] **6.2 Verify container running**
  ```bash
  docker ps | grep alltalk-prod
  ```

- [ ] **6.3 Test API**
  ```bash
  curl http://localhost:7857/api/ready
  ```

- [ ] **6.4 Test Gradio UI**
  Open: http://192.168.0.116:7858

- [ ] **6.5 Performance benchmark**
  ```bash
  time curl -X POST http://localhost:7857/api/tts \
    -H "Content-Type: application/json" \
    -d '{"text": "Hello world", "voice": "female_01.wav"}'
  ```
  Response time: _________

- [ ] **6.6 Monitor resource usage**
  ```bash
  docker stats alltalk-prod
  ```
  CPU: _________
  Memory: _________
  GPU: _________

- [ ] **6.7 Test multiple concurrent requests**
  Expected: Handles load appropriately

- [ ] **6.8 Verify no dev tools present**
  ```bash
  docker exec -it alltalk-prod bash -c "which ipdb"
  ```
  Expected: Not found

### Success Criteria
- ✓ Container runs correctly
- ✓ Performance acceptable
- ✓ Resource usage reasonable
- ✓ No dev tools in production image

### Performance Metrics
| Metric | Value |
|--------|-------|
| API response time | |
| CPU usage | |
| Memory usage | |
| GPU memory | |
| Concurrent requests handled | |

### Issues Encountered
_Document any problems here_

---

## Phase 7: Documentation ⏳

**Status:** Not Started (Do Later)
**Estimated Time:** 30 minutes
**Dependencies:** Phases 1-6 complete

### Tasks

- [ ] **7.1 Update main README.md**
  - Add Docker quick start section
  - Document port mappings
  - Add troubleshooting section

- [ ] **7.2 Update DOCKER_DEV_README.md**
  - Add actual build times
  - Add actual image sizes
  - Add performance benchmarks

- [ ] **7.3 Create deployment checklist**
  - Production deployment steps
  - Security considerations
  - Backup procedures

- [ ] **7.4 Document lessons learned**
  - What worked well
  - What could be improved
  - Tips for future deployments

- [ ] **7.5 Create troubleshooting guide**
  - Common issues and solutions
  - Debug commands
  - Log locations

### Success Criteria
- ✓ Documentation complete and accurate
- ✓ Others can follow deployment process
- ✓ Troubleshooting guide helpful

---

## Quick Reference

### Port Mappings
| Service | Internal | External (Dev) | External (Prod) |
|---------|----------|----------------|-----------------|
| API | 7851 | 7855 | 7857 |
| Gradio UI | 7852 | 7856 | 7858 |
| Original | 7851/7852 | 7851/7852 | N/A |

### Common Commands

**Development:**
```bash
# Start
docker-compose -f docker-compose.dev.yml up -d

# Stop
docker-compose -f docker-compose.dev.yml down

# Restart
docker-compose -f docker-compose.dev.yml restart

# Logs
docker-compose -f docker-compose.dev.yml logs -f

# Enter container
docker exec -it alltalk-dev bash

# Run tests
docker exec -it alltalk-dev bash -c "source conda_env.sh && pytest"
```

**Production:**
```bash
# Run
docker run -d --name alltalk-prod -p 7857:7851 -p 7858:7852 --gpus all alltalk_tts:latest

# Stop
docker stop alltalk-prod

# Remove
docker rm alltalk-prod

# Logs
docker logs -f alltalk-prod
```

### File Locations

**Ubuntu Host:**
```
/mnt/samsungssd/docker/appdata/alltalk/alltalk_test/
├── Dockerfile.dev
├── Dockerfile.prod
├── docker-compose.dev.yml
├── docker-build-dev.sh
├── docker-build-prod.sh
├── confignew.json
├── models/
└── outputs/
```

**Inside Container:**
```
/home/alltalk/
├── tts_server.py (mounted in dev, baked in prod)
├── config.py
├── system/
├── models/ (mounted)
├── outputs/ (mounted)
└── conda_env.sh
```

---

## Issues & Resolutions

### Issue Log
| Date | Phase | Issue | Resolution | Status |
|------|-------|-------|------------|--------|
| | | | | |

---

## Next Steps

**Current Phase:** Phase 1 - Development Docker Setup
**Next Action:** SSH into Ubuntu and verify prerequisites

**When ready to proceed:**
1. SSH into Ubuntu machine
2. Run Phase 1 checklist
3. Report back with results
4. Move to Phase 2

---

## Notes

_Add any additional notes, observations, or reminders here_

---

**Last Updated:** April 21, 2026
**Updated By:** Cascade AI Assistant
