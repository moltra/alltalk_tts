# AllTalk TTS Configuration Architecture

## Overview

AllTalk uses a dual-file configuration system for TTS engine management. This document explains the architecture, merge behavior, and best practices for configuration management.

## Configuration Files

### Primary Configuration File
- **Location**: `config/system/tts_engines.json`
- **Purpose**: Main TTS engine configuration
- **Contains**: 
  - List of available TTS engines
  - Currently loaded engine
  - Selected model for each engine
  - Configuration version

### Secondary Configuration File
- **Location**: `config/system/new_engines.json`
- **Purpose**: Additional/new engine definitions
- **Contains**: 
  - Additional engines not in primary config
  - Example/template configurations
  - Experimental engine definitions

## Configuration Merge Behavior

### Merge Process
The configuration system automatically merges engines from both files at runtime:

1. **Load primary configuration** from `tts_engines.json`
2. **Load secondary configuration** from `new_engines.json`
3. **Merge engines**: Combine unique engines from both files
4. **Remove duplicates**: Engines with same name are not duplicated
5. **Apply merged configuration** to the system

### Merge Logic (from config/app/config.py)
```python
def __handle_loaded_config_engines(self, available_engines):
    available_engine_names = [engine.name for engine in available_engines]
    
    # Getting the engines that are not already part of the available engines:
    new_engines_config = AlltalkNewEnginesConfig.get_instance()
    new_engines = new_engines_config.get_engines_matching(
        lambda eng: eng.name not in available_engine_names
    )
    
    # Merge engines:
    return available_engines + new_engines
```

### Key Merge Rules
- **Engine names must be unique** across both files
- **Primary config takes precedence** for engine_loaded and selected_model
- **Secondary config adds new engines** without overwriting existing ones
- **Both files must be kept synchronized** for consistent behavior

## Configuration Structure

### JSON Schema
```json
{
    "_comment": "Optional documentation about configuration purpose",
    "version": "X.Y",
    "engines_available": [
        {
            "name": "engine_name",
            "selected_model": "model_identifier"
        }
    ],
    "engine_loaded": "current_engine_name",
    "selected_model": "current_model_identifier"
}
```

### Field Descriptions
- `_comment`: Optional documentation field
- `version`: Configuration version identifier (format: X.Y)
- `engines_available`: Array of available engine configurations
- `engine_loaded`: Name of currently active engine
- `selected_model`: Model identifier for current engine

## Available TTS Engines

### XTTS (Primary)
- **Name**: `xtts`
- **Model**: `xtts - xttsv2_2.0.3`
- **Characteristics**: 
  - High quality, multi-lingual
  - Large model size (~2GB)
  - Requires significant GPU memory
  - Supports voice cloning and custom voices

### Piper (Backup)
- **Name**: `piper`
- **Model**: `piper - en_US-joe-medium`
- **Characteristics**:
  - Lightweight, fast
  - Smaller model size (~60MB)
  - Lower GPU memory requirements
  - English language focused
  - Reliable fallback option

### Other Engines (Currently Disabled)
- **vits**: Neural TTS system
- **parler**: Parler TTS mini
- **f5tts**: F5-TTS model

## Configuration Management Best Practices

### Modifying Configuration
1. **Always backup both files** before making changes
2. **Modify both files** to maintain consistency
3. **Validate JSON syntax** after changes
4. **Test configuration loading** before deployment
5. **Document changes** with version increments

### Backup Strategy
```bash
# Create backups
cp tts_engines.json tts_engines.json.backup
cp new_engines.json new_engines.json.backup

# Validate backups
python3 -m json.tool tts_engines.json.backup
python3 -m json.tool new_engines.json.backup
```

### Validation Steps
```bash
# Validate JSON syntax
python3 -m json.tool tts_engines.json
python3 -m json.tool new_engines.json

# Verify model files exist
ls -la /path/to/models/xtts/xttsv2_2.0.3/
ls -la /path/to/models/piper/

# Test configuration loading
docker restart alltalk-dev
curl -s http://localhost:7851/api/currentsettings
```

### Rollback Procedure
```bash
# Restore from backups
cp tts_engines.json.backup tts_engines.json
cp new_engines.json.backup new_engines.json

# Restart service
docker restart alltalk-dev

# Verify restoration
curl -s http://localhost:7851/api/currentsettings
```

## Version Management

### Version Format
- **Format**: `X.Y` (Major.Minor)
- **Major version**: Breaking changes or significant restructure
- **Minor version**: Non-breaking changes, additions, or fixes

### Version History
- **2.1**: XTTS primary with Piper backup, added versioning
- **2.0**: XTTS-only configuration (failed due to tensor errors)
- **1.0**: Original multi-engine configuration

## Troubleshooting

### Configuration Not Loading
1. Check JSON syntax validation
2. Verify file permissions
3. Check for duplicate engine names
4. Review container logs for errors

### Engine Not Available
1. Verify engine exists in both config files
2. Check model files are present
3. Validate model path configuration
4. Review GPU memory availability

### Merge Conflicts
1. Ensure engine names are unique
2. Check for duplicate entries
3. Verify both files are synchronized
4. Review merge logic in config/app/config.py

## Security Considerations

### File Permissions
- Configuration files should be readable by the application
- Restrict write access to administrators
- Use appropriate file permissions (644 for config files)

### Sensitive Information
- Never store API keys or credentials in configuration files
- Use environment variables for sensitive data
- Restrict access to configuration directories

## Performance Considerations

### Engine Selection Impact
- **XTTS**: Higher quality, slower generation, more GPU memory
- **Piper**: Lower quality, faster generation, less GPU memory
- **Selection**: Choose based on use case and available resources

### GPU Memory Management
- XTTS requires ~2GB GPU memory
- Piper requires ~100MB GPU memory
- Monitor GPU usage with `nvidia-smi`
- Consider stopping other GPU processes (e.g., Ollama) when using XTTS

## Future Improvements

### Planned Enhancements
1. **Single configuration file**: Eliminate dual-file complexity
2. **Configuration validation**: Built-in schema validation
3. **Dynamic reloading**: Hot-reload configuration without restart
4. **Web-based configuration**: GUI for engine management
5. **Configuration migration**: Automatic version upgrades

### Refactoring Opportunities
1. Consolidate merge logic into single configuration source
2. Implement configuration schema validation
3. Add configuration change logging
4. Create configuration backup automation
5. Implement configuration rollback automation

## Related Documentation

- **Global Development Rules**: `/home/mark/.codeium/windsurf/memories/global_rules.md`
- **AllTalk Documentation**: Check project README and docs directory
- **Configuration Code**: `config/app/config.py`
- **Engine Implementations**: `system/tts_engines/*/`

## Support and Maintenance

### Configuration Issues
- Check container logs: `docker logs alltalk-dev`
- Validate configuration files
- Review this documentation
- Check global development rules

### Regular Maintenance
- Review configuration versions quarterly
- Update documentation with changes
- Test rollback procedures monthly
- Monitor configuration file sizes and complexity