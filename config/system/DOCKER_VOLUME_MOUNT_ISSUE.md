# Docker Volume Mount Issue - Configuration Changes Not Reflecting in Container

## Problem Description

Configuration file changes made on the host system are not being reflected inside the Docker container, despite the container being configured with volume mounts. The container continues to see old configuration files even after multiple restarts and container rebuilds.

### Current State
- **Host configuration files**: Updated to version 2.1.0 (Piper primary, XTTS available)
- **Container configuration files**: Still showing version 1.0 (all 5 engines available)
- **Expected behavior**: Container should see the updated configuration files from host
- **Actual behavior**: Container sees old/stale configuration files

## Technical Details

### System Information
- **Platform**: Linux 6.17.0-35-generic
- **Docker**: Running with compose
- **Container**: alltalk-dev (alltalk_tts:dev)
- **Mount type**: Bind mounts
- **Filesystem**: ext4 on /dev/nvme0n1p3

### Configuration Files Involved
1. `/mnt/samsungssd/repo/alltalk_tts/config/system/tts_engines.json` (host)
2. `/mnt/samsungssd/repo/alltalk_tts/config/system/new_engines.json` (host)
3. `/mnt/samsungssd/repo/alltalk_tts/system/tts_engines/tts_engines.json` (host)
4. `/mnt/samsungssd/repo/alltalk_tts/system/new_engines.json` (host)

### Container Mount Points
- `/home/alltalk/config` → `/mnt/samsungssd/repo/alltalk_tts/config`
- `/home/alltalk/system` → `/mnt/samsungssd/repo/alltalk_tts/system`

### Application Configuration Loading
The AllTalk application loads configuration from:
- Primary: `/home/alltalk/config/system/tts_engines.json` (via config/app/config.py)
- Secondary: `/home/alltalk/system/new_engines.json` (via config/app/config.py)

## Timeline of Attempts and Results

### Attempt 1: Initial Configuration Changes
**Date**: 2026-06-14 19:32
**Actions**:
- Modified `config/system/tts_engines.json` to remove engines
- Modified `config/system/new_engines.json` to match
- Added volume mount for `new_engines.json` in docker-compose
- Restarted container with `docker restart alltalk-dev`

**Result**: ❌ Container still showed old configuration (all 5 engines)

### Attempt 2: Added Read-Only Flags
**Date**: 2026-06-14 19:35
**Actions**:
- Added `:ro` flags to configuration file mounts
- Restarted container

**Result**: ❌ No change, still showing old configuration

### Attempt 3: File Location Investigation
**Date**: 2026-06-14 19:40
**Actions**:
- Discovered application expects files in different locations
- Moved `new_engines.json` from `config/system/` to `system/`
- Updated docker-compose mount paths
- Restarted container

**Result**: ❌ Application failed to start (file not found error)

### Attempt 4: Path Resolution Fix
**Date**: 2026-06-14 19:45
**Actions**:
- Moved `new_engines.json` back to `config/system/`
- Updated mount paths to match application expectations
- Removed `:ro` flags
- Restarted container

**Result**: ❌ Container started but still showing old configuration

### Attempt 5: Container Rebuild
**Date**: 2026-06-14 19:50
**Actions**:
- Stopped container: `docker compose down`
- Removed container: `docker rm -f alltalk-dev`
- Rebuilt container: `docker compose up -d`
- Waited for full startup (25 seconds)

**Result**: ❌ Container started but still showing old configuration

### Attempt 6: Direct File Investigation
**Date**: 2026-06-14 19:55
**Actions**:
- Checked file timestamps and inodes
- Host file: Modified 19:32, inode 52166793
- Container file: Same inode, same timestamp
- Verified files are actually the same (bind mount working)

**Result**: ⚠️ Bind mount appears to be working, but content doesn't match

### Attempt 7: Multiple File Locations
**Date**: 2026-06-14 20:00
**Actions**:
- Discovered multiple `tts_engines.json` files in different locations
- Host has files in both `config/system/` and `system/tts_engines/`
- Updated both locations to match desired configuration
- Restarted container

**Result**: ❌ Container still showing old configuration

### Attempt 8: Simplified Mount Strategy
**Date**: 2026-06-14 20:05
**Actions**:
- Removed individual file mounts
- Relied on directory mounts only
- Ensured configuration files exist in expected locations
- Rebuilt container

**Result**: ❌ Container started but still showing old configuration

## Observations and Findings

### Key Observations
1. **Bind mounts appear functional**: File inodes and timestamps match between host and container
2. **Directory mounts work**: Other files in mounted directories update correctly
3. **Specific configuration files don't update**: Only `tts_engines.json` and `new_engines.json` affected
4. **Application caching possible**: Application might be caching configuration at startup
5. **Multiple file locations**: Configuration files exist in multiple directories

### File System Analysis
```bash
# Host file status
File: /mnt/samsungssd/repo/alltalk_tts/config/system/tts_engines.json
Size: 491 bytes
Inode: 52166793
Modified: 2026-06-14 19:32:19

# Container file status (via docker exec)
File: /home/alltalk/config/system/tts_engines.json
Size: 491 bytes
Inode: 52166793
Modified: 2026-06-14 19:32:19

# But content shows old configuration when read by application
```

### Mount Analysis
```bash
# Container mounts
/dev/nvme0n1p3 on /home/alltalk/config type ext4 (rw,nosuid,nodev,relatime)
/dev/nvme0n1p3 on /home/alltalk/system type ext4 (rw,nosuid,nodev,relatime)

# Individual file mounts (removed in later attempts)
# Previously had:
# /dev/nvme0n1p3 on /home/alltalk/system/tts_engines/tts_engines.json type ext4
# /dev/nvme0n1p3 on /home/alltalk/system/new_engines.json type ext4
```

### Application Configuration Loading
```python
# From config/app/config.py
class AlltalkTTSEnginesConfig(AbstractJsonConfig, AlltalkTTSEnginesConfigFields):
    def __init__(self, config_path: Path | str = os.path.join(__this_dir, "..", "system", "tts_engines.json")):
        # This resolves to: /home/alltalk/config/system/tts_engines.json
        # NOT: /home/alltalk/system/tts_engines/tts_engines.json

class AlltalkNewEnginesConfig(AbstractJsonConfig, AlltalkTTSEnginesConfigFields):
    def __init__(self, config_path: Path | str = os.path.join(__this_dir, "..", "system", "new_engines.json")):
        # This resolves to: /home/alltalk/config/system/new_engines.json
        # NOT: /home/alltalk/system/new_engines.json
```

## Possible Root Causes

### 1. Application Configuration Caching
**Likelihood**: HIGH
**Description**: The application might cache configuration at startup and not reload it
**Evidence**: 
- Configuration files show correct content when read directly
- Application API returns old configuration
- Application has reload mechanisms that might not be triggered

### 2. Multiple Configuration File Locations
**Likelihood**: MEDIUM
**Description**: Configuration files exist in multiple locations, application might be reading from wrong location
**Evidence**:
- Files exist in both `/home/alltalk/config/system/` and `/home/alltalk/system/tts_engines/`
- Application code references different paths in different contexts
- File system has multiple copies with different content

### 3. Docker Layer Caching
**Likelihood**: LOW
**Description**: Docker might be caching file system layers
**Evidence**:
- Container rebuild didn't resolve issue
- File inodes match between host and container
- Bind mounts should bypass layer caching

### 4. File System Caching
**Likelihood**: LOW
**Description**: OS file system cache might be serving stale content
**Evidence**:
- File timestamps and inodes match
- Direct file reads show correct content
- Other files in same directories update correctly

### 5. Application Startup Sequence
**Likelihood**: MEDIUM
**Description**: Application might load configuration before mounts are fully established
**Evidence**:
- Application has complex startup sequence
- Configuration loading happens early in startup
- Container logs show configuration loading during startup

## What Else Could Be Tried

### Immediate Attempts

#### 1. Force Application Configuration Reload
```bash
# Try to trigger application reload via API
curl -X POST http://localhost:7851/api/reload
curl -X POST http://localhost:7851/api/enginereload

# Or send SIGHUP to process
docker exec alltalk-dev kill -HUP 1
```

#### 2. Clear Application Cache
```bash
# Find and remove any cache files
docker exec alltalk-dev find /home/alltalk -name "*.cache" -delete
docker exec alltalk-dev find /home/alltalk -name "__pycache__" -type d -exec rm -rf {} +

# Restart container
docker restart alltalk-dev
```

#### 3. Verify File Content Directly in Container
```bash
# Read file content directly (not through application)
docker exec alltalk-dev cat /home/alltalk/config/system/tts_engines.json
docker exec alltalk-dev cat /home/alltalk/system/new_engines.json

# Compare with host
diff /mnt/samsungssd/repo/alltalk_tts/config/system/tts_engines.json \
     <(docker exec alltalk-dev cat /home/alltalk/config/system/tts_engines.json)
```

#### 4. Check Application File Descriptors
```bash
# Check what files the application has open
docker exec alltalk-dev lsof -p 1
docker exec alltalk-dev ls -la /proc/1/fd | grep tts_engines
```

#### 5. Mount with Different Options
```yaml
# Try different mount options in docker-compose
volumes:
  - /mnt/samsungssd/repo/alltalk_tts/config:/home/alltalk/config:cached
  - /mnt/samsungssd/repo/alltalk_tts/config:/home/alltalk/config:delegated
  - /mnt/samsungssd/repo/alltalk_tts/config:/home/alltalk/config:rw,noatime
```

### Deeper Investigation

#### 6. Enable Docker Debug Logging
```bash
# Enable Docker debug logging
docker-compose -f alltalk-tts.yml --verbose up
dockerd --debug
```

#### 7. Use strace to Monitor File Access
```bash
# Monitor file system access in container
docker exec alltalk-dev strace -f -e trace=open,openat,read,write python tts_server.py
```

#### 8. Check for Overlay2 Issues
```bash
# Check Docker storage driver
docker info | grep "Storage Driver"

# Check overlay2 mount points
mount | grep overlay
docker inspect alltalk-dev | grep -A 20 Mounts
```

#### 9. Test with Minimal Container
```bash
# Create minimal container to test bind mount
docker run -it --rm \
  -v /mnt/samsungssd/repo/alltalk_tts/config/system/tts_engines.json:/test/config.json \
  alpine cat /test/config.json
```

#### 10. Check for File Locking
```bash
# Check if files are locked
docker exec alltalk-dev fuser /home/alltalk/config/system/tts_engines.json
docker exec alltalk-dev ls -la /home/alltalk/config/system/tts_engines.json
```

### Alternative Approaches

#### 11. Use Docker Configs/Secrets
```yaml
# Instead of bind mounts, use Docker configs
configs:
  tts_config:
    file: /mnt/samsungssd/repo/alltalk_tts/config/system/tts_engines.json

services:
  alltalk-dev:
    configs:
      - tts_config
```

#### 12. Use Environment Variables for Configuration
```bash
# Pass configuration via environment variables
environment:
  - TTS_ENGINES_CONFIG='{"engines_available":[...]}'
```

#### 13. Copy Files at Container Startup
```yaml
# Use entrypoint script to copy files
entrypoint: >
  sh -c "cp /host/config/* /app/config/ && exec python tts_server.py"
volumes:
  - /mnt/samsungssd/repo/alltalk_tts/config:/host/config:ro
```

#### 14. Use Named Volumes Instead of Bind Mounts
```yaml
# Create named volume and copy files
volumes:
  tts_config:
    driver: local
    driver_opts:
      type: none
      device: /mnt/samsungssd/repo/alltalk_tts/config
      o: bind
```

#### 15. Rebuild Image Without Cache
```bash
# Force rebuild without layer cache
docker-compose build --no-cache
docker-compose up -d
```

## Diagnostic Commands

### Current State Verification
```bash
# Check current configuration in container
curl -s http://localhost:7851/api/currentsettings | jq

# Check file content directly
docker exec alltalk-dev cat /home/alltalk/config/system/tts_engines.json

# Check mounts
docker exec alltalk-dev mount | grep alltalk

# Check file inodes
docker exec alltalk-dev stat /home/alltalk/config/system/tts_engines.json
stat /mnt/samsungssd/repo/alltalk_tts/config/system/tts_engines.json
```

### Application Process Analysis
```bash
# Check application process
docker exec alltalk-dev ps aux

# Check environment variables
docker exec alltalk-dev env | grep -i config

# Check working directory
docker exec alltalk-dev pwd
docker exec alltalk-dev ls -la
```

### Docker Inspection
```bash
# Detailed container inspection
docker inspect alltalk-dev | jq '.[0].Mounts'

# Check container filesystem
docker exec alltalk-dev find /home/alltalk -name "*engines*.json"

# Check bind mount details
docker inspect alltalk-dev | jq '.[0].HostConfig.Binds'
```

## Next Steps and Recommendations

### Immediate Priority
1. **Verify actual file content in container** - Use direct cat commands to confirm what the container actually sees
2. **Test application reload** - Try API endpoints that might trigger configuration reload
3. **Check application startup logs** - Look for configuration loading messages and errors

### Short-term Solutions
1. **Use entrypoint script** - Copy configuration files at container startup to ensure correct content
2. **Environment variable override** - Pass configuration via environment variables as fallback
3. **Restart application process** - Try restarting the application process within the container

### Long-term Solutions
1. **Refactor configuration loading** - Make application watch for file changes and reload automatically
2. **Single source of truth** - Eliminate multiple configuration file locations
3. **Configuration validation** - Add startup validation to detect configuration mismatches
4. **Health check endpoint** - Add endpoint to verify configuration loading

### Investigation Priority
1. **HIGH**: Verify actual file content vs. application-reported content
2. **HIGH**: Test application reload mechanisms
3. **MEDIUM**: Check for application caching
4. **MEDIUM**: Investigate multiple file locations
5. **LOW**: Docker layer caching investigation

## Additional Context

### Configuration System Architecture
The AllTalk application uses a dual-file configuration system:
- **Primary configuration**: Loaded from `config/system/tts_engines.json`
- **Secondary configuration**: Loaded from `system/new_engines.json`
- **Merge behavior**: Engines from both files are merged at runtime
- **Version management**: Configuration includes version field for tracking changes

### Recent Changes
- **Version 2.1.0**: Piper primary with XTTS available
- **Version 1.0**: Original multi-engine configuration (all 5 engines)
- **Changes**: Removed parler, vits, f5tts engines; fixed Piper model identifier; added versioning

### System Dependencies
- **GPU**: NVIDIA RTX 2060 with CUDA 12.8
- **Ollama**: Previously using GPU memory, now stopped
- **Memory**: 6GB GPU total, ~2GB available for XTTS
- **Storage**: Local NVMe SSD with ext4 filesystem

## Contact and Support

### Relevant Documentation
- Docker bind mounts: https://docs.docker.com/storage/bind-mounts/
- Docker compose volumes: https://docs.docker.com/compose/compose-file/compose-file-v3/#volumes
- AllTalk configuration: `/mnt/samsungssd/repo/alltalk_tts/config/system/CONFIGURATION_ARCHITECTURE.md`
- Change log: `/mnt/samsungssd/repo/alltalk_tts/config/system/CHANGELOG_v2.1.md`

### System Information
- **Docker version**: Check with `docker version`
- **Docker Compose version**: Check with `docker compose version`
- **Kernel version**: Linux 6.17.0-35-generic
- **Distribution**: Check with `cat /etc/os-release`

---

**Document created**: 2026-06-14 20:15  
**Last updated**: 2026-06-14 20:15  
**Status**: Investigation ongoing, awaiting user review