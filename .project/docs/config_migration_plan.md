# Config File Consolidation Migration Plan

**Date**: 2026-04-22
**Status**: In Progress
**Objective**: Consolidate scattered config files into a centralized `config/` directory structure

---

## Phase 1: File Structure Changes (COMPLETED)

### Completed Actions

✅ **Created new directory structure:**
```
config/
├── app/                    # Application-level configs
│   ├── confignew.json
│   ├── mem_config.json
│   └── config.py
├── docker/                 # Docker-specific configs
│   ├── docker_confignew.json
│   ├── docker_default_confignew.json
│   ├── docker_default_mem_config.json
│   └── docker_mem_config.json
├── engines/                # TTS engine configs
│   ├── xtts/
│   │   ├── model_settings.json
│   │   └── available_models.json
│   ├── rvc/
│   │   └── configs/ (entire directory)
│   ├── vits/
│   │   ├── model_settings.json
│   │   └── available_models.json
│   ├── piper/
│   │   ├── model_settings.json
│   │   └── available_models.json
│   ├── parler/
│   │   ├── model_settings.json
│   │   └── available_models.json
│   ├── f5tts/
│   │   ├── model_settings.json
│   │   └── available_models.json
│   └── template-tts-engine/
│       ├── model_settings.json
│       └── available_models.json
└── system/                 # System-level configs
    ├── logging_config.py
    └── tgwui_remote_config.json
```

✅ **Moved files from old locations to new structure**

---

## Phase 2: Import Updates (PENDING)

### 2.1 Update Python Module Imports

**Files requiring import updates:**

1. **Main application files:**
   - `tts_server.py` ✅ (COMPLETED - updated to `from config.app.config import`)
   - `script.py` - Needs update
   - `tts_mem.py` - Needs update

2. **System files:**
   - `system/tts_engines/xtts/model_engine.py` - Needs update
   - `system/tts_engines/rvc/infer/infer.py` - Needs update
   - `system/config/firstrun.py` - Needs update
   - `system/config/firstrun_tgwui.py` - Needs update
   - `system/state_manager.py` - Needs update
   - `system/tts_engines/template-tts-engine/template_engine.py` - Needs update
   - `system/proxy_module/twisted_server.py` - Needs update

3. **Test files:**
   - `tests/conftest.py` - Needs update
   - `tests/test_api_endpoints.py` - Needs update
   - `tests/test_cors_config.py` - Needs update
   - `tests/test_config.py` - Needs update
   - `test/test_config.py` - Needs update

**Import Changes Required:**

| Old Import | New Import |
|------------|------------|
| `from config import` | `from config.app.config import` |
| `import config` | `from config.app import config` |
| `from system.logging_config import` | `from config.system.logging_config import` |
| `from system.tts_engines.rvc.configs.config import` | `from config.engines.rvc.configs.config import` |

### 2.2 Update File Path References

**Files requiring path updates for `confignew.json`:**
- `system/tts_engines/xtts/model_engine.py`
- `system/tts_engines/vits/model_engine.py`
- `system/tts_engines/template-tts-engine/template_engine.py`
- `system/tts_engines/template-tts-engine/model_engine.py`
- `system/tts_engines/piper/model_engine.py`
- `system/tts_engines/f5tts/model_engine.py`
- `system/tts_engines/parler/model_engine.py`
- `system/TGWUI_Extension/script.py`
- `system/gradio_pages/themes/loadThemes.py`
- `system/config/firstrun_tgwui.py`
- `system/config/firstrun.py`
- `script.py`

**Path Changes Required:**
| Old Path | New Path |
|-----------|----------|
| `confignew.json` | `config/app/confignew.json` |
| `mem_config.json` | `config/app/mem_config.json` |
| `docker_confignew.json` | `config/docker/docker_confignew.json` |
| `docker_default_confignew.json` | `config/docker/docker_default_confignew.json` |

**Files requiring path updates for `model_settings.json`:**
- `tts_server.py`
- `tests/test_xtts_engine.py`
- `system/tts_engines/xtts/xtts_settings_page.py`
- `system/tts_engines/xtts/model_engine.py`
- `system/tts_engines/vits/vits_settings_page.py`
- `system/tts_engines/vits/model_engine.py`
- `system/tts_engines/template-tts-engine/template_engine.py`
- `system/tts_engines/template-tts-engine/model_engine.py`
- `system/tts_engines/template-tts-engine/modelname_settings_page.py`
- `system/tts_engines/piper/model_engine.py`
- `system/tts_engines/piper/piper_settings_page.py`
- `system/tts_engines/parler/parler_settings_page.py`
- `system/tts_engines/parler/model_engine.py`
- `system/tts_engines/f5tts/model_engine.py`
- `system/tts_engines/f5tts/f5tts_settings_page.py`
- `script.py`

**Path Changes Required:**
| Old Path | New Path |
|-----------|----------|
| `system/tts_engines/{engine}/model_settings.json` | `config/engines/{engine}/model_settings.json` |

**Files requiring path updates for `available_models.json`:**
- Similar to model_settings.json, located in same engine directories

**Path Changes Required:**
| Old Path | New Path |
|-----------|----------|
| `system/tts_engines/{engine}/available_models.json` | `config/engines/{engine}/available_models.json` |

---

## Phase 3: Implementation Strategy

### 3.1 Implementation Order

**Priority 1: Critical Application Files**
1. Update `tts_server.py` imports ✅
2. Update `script.py` imports and paths
3. Update `tts_mem.py` imports and paths

**Priority 2: Engine Model Files**
4. Update all engine `model_engine.py` files (xtts, vits, piper, parler, f5tts, template-tts-engine)
5. Update engine settings pages
6. Update RVC-specific config references

**Priority 3: System Configuration Files**
7. Update `system/config/firstrun.py`
8. Update `system/config/firstrun_tgwui.py`
9. Update `system/state_manager.py`
10. Update `system/TGWUI_Extension/script.py`

**Priority 4: Test Files**
11. Update all test files to use new paths
12. Verify all tests pass

### 3.2 Search and Replace Patterns

**For Python imports:**
```bash
# Replace config imports
find . -name "*.py" -type f -exec sed -i 's/from config import/from config.app.config import/g' {} +
find . -name "*.py" -type f -exec sed -i 's/import config/from config.app import config/g' {} +
```

**For path references:**
```bash
# Replace confignew.json paths
find . -name "*.py" -type f -exec sed -i 's|"confignew.json"|"config/app/confignew.json"|g' {} +
find . -name "*.py" -type f -exec sed -i "s|'confignew.json'|'config/app/confignew.json'|g" {} +

# Replace model_settings.json paths
find . -name "*.py" -type f -exec sed -i 's|system/tts_engines/\([^/]*\)/model_settings.json|config/engines/\1/model_settings.json|g' {} +

# Replace available_models.json paths
find . -name "*.py" -type f -exec sed -i 's|system/tts_engines/\([^/]*\)/available_models.json|config/engines/\1/available_models.json|g' {} +
```

---

## Phase 4: Testing Strategy

### 4.1 Unit Tests
- Run `pytest tests/test_config.py` - Verify config loading
- Run `pytest tests/test_xtts_engine.py` - Verify XTTS engine config access
- Run `pytest tests/test_api_endpoints.py` - Verify API endpoint config access

### 4.2 Integration Tests
- Start `tts_server.py` - Verify server loads configs correctly
- Start `script.py` - Verify Gradio UI loads configs correctly
- Test model loading - Verify engines can access their config files

### 4.3 Manual Testing Checklist
- [ ] Application starts without errors
- [ ] Config files load correctly from new locations
- [ ] All TTS engines can load their model_settings.json
- [ ] Docker configs work in Docker environment
- [ ] Test suite passes completely
- [ ] No broken imports or path references

---

## Phase 5: Rollback Plan

If migration causes critical issues:

1. **Immediate Rollback:**
   ```bash
   # Move files back to original locations
   mv config/app/confignew.json confignew.json
   mv config/app/mem_config.json mem_config.json
   mv config/app/config.py config.py
   mv config/docker/* ./
   mv config/engines/*/model_settings.json system/tts_engines/*/model_settings.json
   mv config/engines/*/available_models.json system/tts_engines/*/available_models.json
   mv config/system/logging_config.py system/logging_config.py
   mv config/engines/rvc/configs system/tts_engines/rvc/configs
   ```

2. **Revert Code Changes:**
   ```bash
   git checkout -- .  # Revert all code changes
   ```

3. **Cleanup:**
   ```bash
   rm -rf config/  # Remove new config directory
   ```

---

## Phase 6: Documentation Updates

After successful migration:

1. **Update README.md** - Document new config structure
2. **Update Dockerfile** - Update COPY commands for config files
3. **Update docker-compose.yml** - Update volume mounts
4. **Update CODEMAP.md** - Reflect new structure
5. **Create CONFIG_STRUCTURE.md** - Detailed documentation of config organization

---

## Phase 7: Migration Script (Optional)

Create a Python script to automate the migration:

```python
#!/usr/bin/env python3
"""
Automated config file migration script
"""
import shutil
from pathlib import Path

def migrate_configs():
    """Move config files to new structure"""
    # Implementation details...

def update_imports():
    """Update Python imports in codebase"""
    # Implementation details...

def update_paths():
    """Update file path references"""
    # Implementation details...

if __name__ == "__main__":
    migrate_configs()
    update_imports()
    update_paths()
    print("Migration complete!")
```

---

## Status Tracking

- [x] Phase 1: File Structure Changes
- [ ] Phase 2: Import Updates
  - [ ] 2.1 Update Python Module Imports
  - [ ] 2.2 Update File Path References
- [ ] Phase 3: Implementation
- [ ] Phase 4: Testing
- [ ] Phase 5: Rollback (if needed)
- [ ] Phase 6: Documentation Updates
- [ ] Phase 7: Migration Script (optional)

---

## Notes

- **RVC Engine**: Has a different structure with `configs/` directory instead of individual config files. The entire `configs/` directory was moved.
- **Test Files**: Some test files may need special handling for mock paths.
- **Docker**: Dockerfiles and docker-compose files will need updates to reflect new structure.
- **Backward Compatibility**: Consider adding symlinks or fallback logic if needed for backward compatibility.
