# AllTalk TTS v2 - Comprehensive Refactoring Plan

**Created:** 2025-04-21  
**Objective:** Fix all identified issues and standardize testing using pytest and Loguru  
**Estimated Duration:** 4-6 weeks (depending on team size and availability)

---

## Overview

This plan addresses all 23 issues identified in the code review and establishes a standardized testing and logging infrastructure using pytest and Loguru. The work is organized into 9 phases with clear priorities and dependencies.

---

## Phase 1: Critical Security Fixes (Week 1)

### 1.1 Fix CORS Configuration
**File:** `tts_server.py:229`  
**Priority:** Critical  
**Effort:** 2 hours

**Tasks:**
- [ ] Create environment variable for allowed origins
- [ ] Update CORS middleware to use specific origins
- [ ] Add configuration option in `confignew.json` for CORS settings
- [ ] Document CORS configuration in README
- [ ] Add tests for CORS behavior

**Implementation:**
```python
# Add to config.py
class AlltalkConfigCorsSettings(BaseModel):
    allowed_origins: List[str] = ["http://localhost:7852", "http://localhost:3000"]
    allow_credentials: bool = True

# Update tts_server.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_settings.allowed_origins,
    allow_credentials=config.cors_settings.allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Testing:**
- Test that allowed origins can access API
- Test that disallowed origins are rejected
- Test with credentials enabled/disabled

---

### 1.2 Secure Subprocess Execution
**File:** `diagnostics.py:1015`  
**Priority:** Critical  
**Effort:** 4 hours

**Tasks:**
- [ ] Remove `shell=True` from subprocess calls
- [ ] Implement command validation whitelist
- [ ] Sanitize user input before execution
- [ ] Add error handling for subprocess failures
- [ ] Document security measures

**Implementation:**
```python
# Create command whitelist
ALLOWED_PIP_COMMANDS = [
    "install",
    "uninstall",
    "list",
    "show",
    "freeze"
]

# Validate and execute safely
def execute_pip_command(command: str):
    parts = command.split()
    if not parts or parts[0] not in ALLOWED_PIP_COMMANDS:
        raise ValueError(f"Command not allowed: {parts[0] if parts else 'empty'}")
    
    # Use list instead of shell=True
    result = subprocess.run(
        [sys.executable, "-m", "pip"] + parts[1:],
        capture_output=True,
        text=True,
        check=True
    )
    return result
```

**Testing:**
- Test allowed commands execute successfully
- Test disallowed commands are rejected
- Test command injection attempts are blocked
- Test error handling

---

### 1.3 Begin Global State Refactoring
**Files:** `tts_server.py`, `tts_mem.py`, `finetune.py`, `script.py`  
**Priority:** Critical  
**Effort:** 40 hours (ongoing across phases)

**Tasks:**
- [ ] Create `StateManager` class for application state
- [ ] Refactor `config` and `tts_engines_config` to use dependency injection
- [ ] Create `ServerState` class for tts_server.py globals
- [ ] Create `MEMState` class for tts_mem.py globals
- [ ] Update function signatures to accept state objects
- [ ] Add tests for state management

**Implementation:**
```python
# Create system/state_manager.py
class StateManager:
    """Centralized state management for AllTalk application"""
    
    def __init__(self):
        self._config: Optional[AlltalkConfig] = None
        self._tts_engines_config: Optional[AlltalkTTSEnginesConfig] = None
        self._infer_pipeline = None
        self._lock = Lock()
    
    @property
    def config(self) -> AlltalkConfig:
        if self._config is None:
            self._config = AlltalkConfig.get_instance()
        return self._config
    
    @property
    def tts_engines_config(self) -> AlltalkTTSEnginesConfig:
        if self._tts_engines_config is None:
            self._tts_engines_config = AlltalkTTSEnginesConfig.get_instance()
        return self._tts_engines_config
    
    async def reload_config(self, force: bool = False):
        async with self._lock:
            self._config = AlltalkConfig.get_instance(force_reload=force)
            self._tts_engines_config = AlltalkTTSEnginesConfig.get_instance(force_reload=force)

# Global state manager instance
state_manager = StateManager()
```

**Testing:**
- Test state isolation between tests
- Test concurrent access with locks
- Test config reload functionality

---

## Phase 2: Logging Standardization (Week 1-2)

### 2.1 Replace logging.disable with Loguru Setup
**Files:** Multiple files  
**Priority:** High  
**Effort:** 8 hours

**Tasks:**
- [ ] Remove all `logging.disable(logging.WARNING)` calls
- [ ] Install Loguru dependency
- [ ] Create centralized logging configuration
- [ ] Configure Loguru with rotation, retention, and formatting
- [ ] Add environment-based log level configuration

**Implementation:**
```python
# Create system/logging_config.py
from loguru import logger
import sys

def setup_logging(log_level: str = "INFO", log_file: str = "alltalk.log"):
    """Configure Loguru for AllTalk application"""
    
    # Remove default handler
    logger.remove()
    
    # Add console handler with colors
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=log_level,
        colorize=True
    )
    
    # Add file handler with rotation
    logger.add(
        log_file,
        rotation="500 MB",
        retention="10 days",
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=log_level
    )
    
    # Add error file handler
    logger.add(
        "errors.log",
        rotation="100 MB",
        retention="30 days",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    )
    
    return logger

# Initialize at application startup
alltalk_logger = setup_logging()
```

**Testing:**
- Test log levels are respected
- Test log rotation works
- Test error logs go to separate file
- Test console formatting

---

### 2.2 Replace Print Statements with Loguru
**Files:** `tts_server.py`, `tts_mem.py`, and others  
**Priority:** High  
**Effort:** 16 hours

**Tasks:**
- [ ] Audit all print statements in codebase
- [ ] Replace with appropriate Loguru calls (debug, info, warning, error)
- [ ] Maintain component-based prefixes for filtering
- [ ] Update color coding to use Loguru's built-in features

**Implementation:**
```python
# Update print_message function in tts_server.py
from system.logging_config import alltalk_logger as logger

def print_message(message: str, message_type: str = "standard", component: str = "TTS"):
    """Centralized logging function using Loguru"""
    prefix = f"[{config.branding}{component}]"
    full_message = f"{prefix} {message}"
    
    if message_type.startswith("debug_"):
        debug_flag = getattr(config.debugging, message_type, False)
        if not debug_flag:
            return
        logger.debug(full_message)
    elif message_type == "warning":
        logger.warning(full_message)
    elif message_type == "error":
        logger.error(full_message)
    else:
        logger.info(full_message)
```

**Testing:**
- Test all message types log correctly
- Test debug flags work as expected
- Test component prefixes are preserved

---

### 2.3 Create Centralized Logging Configuration
**File:** `system/logging_config.py`  
**Priority:** High  
**Effort:** 4 hours

**Tasks:**
- [ ] Create logging configuration module
- [ ] Add configuration options for log levels, file paths
- [ ] Support JSON structured logging option
- [ ] Add correlation ID support for request tracking
- [ ] Document logging configuration

**Implementation:**
```python
# system/logging_config.py
from loguru import logger
import sys
from pathlib import Path
from typing import Optional
import uuid

class LoggingConfig:
    """Centralized logging configuration for AllTalk"""
    
    def __init__(
        self,
        log_level: str = "INFO",
        log_file: Optional[str] = None,
        structured: bool = False,
        enable_correlation: bool = True
    ):
        self.log_level = log_level
        self.log_file = log_file or "alltalk.log"
        self.structured = structured
        self.enable_correlation = enable_correlation
        self._correlation_id: Optional[str] = None
    
    def setup(self):
        """Configure Loguru handlers"""
        logger.remove()
        
        # Console handler
        console_format = self._get_console_format()
        logger.add(
            sys.stdout,
            format=console_format,
            level=self.log_level,
            colorize=True
        )
        
        # File handler
        logger.add(
            self.log_file,
            rotation="500 MB",
            retention="10 days",
            compression="zip",
            format=self._get_file_format(),
            level=self.log_level
        )
        
        return logger
    
    def _get_console_format(self) -> str:
        if self.structured:
            return "{message}"
        return "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    
    def _get_file_format(self) -> str:
        if self.structured:
            return "{message}"
        return "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    
    def set_correlation_id(self, correlation_id: str):
        """Set correlation ID for request tracking"""
        self._correlation_id = correlation_id
    
    def get_correlation_id(self) -> str:
        """Get or generate correlation ID"""
        if self._correlation_id is None and self.enable_correlation:
            self._correlation_id = str(uuid.uuid4())
        return self._correlation_id or ""
```

**Testing:**
- Test configuration initialization
- Test correlation ID generation
- Test structured vs standard logging

---

## Phase 3: Error Handling (Week 2)

### 3.1 Replace Bare Except Clauses
**Files:** `tts_mem.py:1090`, `system/tts_engines/rvc/train/utils.py:67`, `system/tts_engines/rvc/train/train.py:291`, `system/ft_tokenizer/tokenizer.py:560`, `finetune.py:167,177`  
**Priority:** High  
**Effort:** 8 hours

**Tasks:**
- [ ] Identify all bare except clauses
- [ ] Replace with specific exception types
- [ ] Add logging for caught exceptions
- [ ] Ensure SystemExit and KeyboardInterrupt propagate

**Implementation:**
```python
# Before (bad)
try:
    # some code
except:
    pass

# After (good)
try:
    # some code
except (ValueError, KeyError) as e:
    logger.error(f"Expected error occurred: {e}")
except Exception as e:
    logger.exception(f"Unexpected error: {e}")
    raise  # Re-raise unexpected errors
```

**Testing:**
- Test specific exceptions are caught
- Test unexpected exceptions are logged and re-raised
- Test KeyboardInterrupt still exits properly

---

### 3.2 Establish Consistent Error Handling Policy
**Files:** Throughout codebase  
**Priority:** High  
**Effort:** 12 hours

**Tasks:**
- [ ] Create custom exception classes in `system/exceptions.py`
- [ ] Define error handling decorator
- [ ] Document error handling patterns
- [ ] Apply consistent error handling across codebase

**Implementation:**
```python
# Create system/exceptions.py
class AllTalkError(Exception):
    """Base exception for AllTalk application"""
    pass

class ConfigurationError(AllTalkError):
    """Raised when configuration is invalid"""
    pass

class TTSEngineError(AllTalkError):
    """Raised when TTS engine fails"""
    pass

class ModelLoadError(TTSEngineError):
    """Raised when model fails to load"""
    pass

class AudioProcessingError(AllTalkError):
    """Raised when audio processing fails"""
    pass

class APIError(AllTalkError):
    """Raised when API request fails"""
    pass

# Create error handling decorator
# system/error_handler.py
from functools import wraps
from loguru import logger

def handle_errors(component: str = "TTS"):
    """Decorator for consistent error handling"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except AllTalkError as e:
                logger.error(f"[{component}] {type(e).__name__}: {e}")
                raise
            except Exception as e:
                logger.exception(f"[{component}] Unexpected error in {func.__name__}")
                raise AllTalkError(f"Unexpected error: {e}") from e
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except AllTalkError as e:
                logger.error(f"[{component}] {type(e).__name__}: {e}")
                raise
            except Exception as e:
                logger.exception(f"[{component}] Unexpected error in {func.__name__}")
                raise AllTalkError(f"Unexpected error: {e}") from e
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator
```

**Testing:**
- Test custom exceptions work correctly
- Test decorator catches and logs errors
- Test error propagation works

---

### 3.3 Replace os.system Calls
**File:** `diagnostics.py:1037, 1039`  
**Priority:** High  
**Effort:** 2 hours

**Tasks:**
- [ ] Replace `os.system("cls")` with cross-platform solution
- [ ] Replace `os.system("clear")` with cross-platform solution
- [ ] Consider if screen clearing is necessary

**Implementation:**
```python
# Use platform-specific library
from loguru import logger

def clear_screen():
    """Clear terminal screen cross-platform"""
    try:
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
    except Exception as e:
        logger.warning(f"Failed to clear screen: {e}")
```

**Testing:**
- Test screen clearing works on Windows
- Test screen clearing works on Linux
- Test error handling when clearing fails

---

## Phase 4: Code Quality (Week 2-3)

### 4.1 Add Type Hints
**Files:** Throughout codebase  
**Priority:** Medium  
**Effort:** 24 hours

**Tasks:**
- [ ] Add type hints to all public functions
- [ ] Add type hints to class methods
- [ ] Use typing module for complex types
- [ ] Add type hints to configuration classes
- [ ] Enable mypy in development

**Implementation:**
```python
# Example for tts_server.py
from typing import Optional, Dict, List, Union
from pathlib import Path

def load_config(force_reload: bool = False) -> None:
    """Initialize all configuration instances"""
    global config, tts_engines_config
    config = AlltalkConfig.get_instance(force_reload)
    tts_engines_config = AlltalkTTSEnginesConfig.get_instance(force_reload)
    after_config_load()

async def apifunction_reload(request: Request) -> Response:
    """Handle API request to change TTS model"""
    debug_func_entry()
    
    if model_change_lock.locked():
        print_message("Model change already in progress", "debug_api", "API")
        return Response(
            content=json.dumps({"status": "model-is currently changing"}),
            media_type="application/json"
        )
    
    async with model_change_lock:
        requested_model = request.query_params.get("tts_method")
        if requested_model not in model_engine.available_models:
            print_message(f"Invalid TTS method requested: {requested_model}", "error", "API")
            return {"status": "error", "message": "Invalid TTS method specified"}
        
        print_message(f"Attempting to change model to: {requested_model}", "debug_api", "API")
        success = await model_engine.handle_tts_method_change(requested_model)
        
        if success:
            model_engine.current_model_loaded = requested_model
            print_message(f"Model successfully changed to: {requested_model}", "debug_api", "API")
            return Response(
                content=json.dumps({"status": "model-success"}),
                media_type="application/json"
            )
        
        print_message(f"Failed to change model to: {requested_model}", "error", "API")
        return Response(
            content=json.dumps({"status": "model-failure"}),
            media_type="application/json"
        )
```

**Testing:**
- Run mypy to check type correctness
- Fix type errors as they arise

---

### 4.2 Split Large Files
**Files:** `diagnostics.py` (~1,400 lines), `script.py` (~4,965 lines), `tts_server.py` (~2,620 lines), `finetune.py` (~4,810 lines)  
**Priority:** Medium  
**Effort:** 40 hours

**Tasks:**
- [ ] Split `diagnostics.py` into focused modules
- [ ] Split `script.py` into UI, logic, and integration modules
- [ ] Split `tts_server.py` into endpoint modules
- [ ] Split `finetune.py` into data processing, training, and UI modules
- [ ] Maintain backward compatibility during transition

**Implementation Plan for script.py:**
```
system/
  gradio_ui/
    __init__.py
    main_ui.py          # Main Gradio interface
    tts_generator.py    # TTS generation UI
    bulk_generator.py   # Bulk operations UI
    settings_ui.py      # Settings pages
  gradio_logic/
    __init__.py
    tts_handler.py      # TTS generation logic
    audio_processor.py  # Audio processing
    transcription.py   # Transcription logic
  integrations/
    __init__.py
    tgwui_integration.py
    sillytavern_integration.py
```

**Implementation Plan for tts_server.py:**
```
system/
  api/
    __init__.py
    app.py              # FastAPI app setup
    endpoints/
      __init__.py
      tts.py            # TTS generation endpoints
      models.py         # Model management endpoints
      config.py         # Configuration endpoints
      audio.py          # Audio serving endpoints
      rvc.py            # RVC endpoints
    middleware/
      __init__.py
      cors.py           # CORS configuration
      auth.py           # Authentication (future)
```

**Testing:**
- Ensure all imports work after split
- Run existing tests to verify no breakage
- Add tests for new modules

---

### 4.3 Fix Pylint Warnings
**Files:** Throughout codebase  
**Priority:** Medium  
**Effort:** 16 hours

**Tasks:**
- [ ] Fix dangerous-default-value warnings
- [ ] Fix unused-variable warnings
- [ ] Fix unused-argument warnings
- [ ] Fix broad-exception-caught warnings
- [ ] Fix assignment-from-no-return warnings
- [ ] Remove unnecessary pylint disable comments

**Implementation:**
```python
# Fix dangerous-default-value
def __init__(self, items: Optional[List] = None):
    self.items = items if items is not None else []

# Fix unused-variable
output_file_path, _, _ = await tts_handle_output_paths(...)

# Fix unused-argument
async def startup_shutdown(_app: FastAPI) -> AsyncGenerator:
    """Initialize model engine and handle graceful shutdown"""
    debug_func_entry()
    try:
        await model_engine.setup()
    except FileNotFoundError as e:
        print_message(f"Error during setup: {e}", "error")
    yield
```

**Testing:**
- Run pylint with strict mode
- Address all warnings
- Update pylint configuration if needed

---

### 4.4 Remove Unused Variables and Fix Issues
**Files:** `tts_server.py`, `trainer_alltalk/trainer.py`  
**Priority:** Medium  
**Effort:** 4 hours

**Tasks:**
- [ ] Remove unused variables
- [ ] Fix dangerous default values
- [ ] Fix assignment from no-return
- [ ] Add tests for previously unused code if needed

---

## Phase 5: Testing Infrastructure (Week 3)

### 5.1 Set Up Pytest Configuration
**File:** `pytest.ini` (already exists, needs enhancement)  
**Priority:** High  
**Effort:** 4 hours

**Tasks:**
- [ ] Enhance existing pytest.ini configuration
- [ ] Add pytest plugins (pytest-asyncio, pytest-cov, pytest-loguru)
- [ ] Configure test discovery patterns
- [ ] Set up coverage configuration

**Implementation:**
```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --strict-markers
    --strict-config
    --cov=.
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
    -v
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
    gpu: Tests requiring GPU
    audio: Tests requiring audio output
asyncio_mode = auto
log_cli = true
log_cli_level = INFO
log_cli_format = %(asctime)s [%(levelname)8s] %(message)s
log_cli_date_format = %Y-%m-%d %H:%M:%S
```

**Requirements additions:**
```
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0
pytest-loguru>=0.2.0
pytest-mock>=3.11.0
```

**Testing:**
- Run pytest to verify configuration
- Test coverage reporting works
- Test async tests work

---

### 5.2 Create Test Fixtures and conftest.py
**File:** `tests/conftest.py`  
**Priority:** High  
**Effort:** 8 hours

**Tasks:**
- [ ] Create conftest.py with common fixtures
- [ ] Add config fixture
- [ ] Add temp directory fixture
- [ ] Add mock model engine fixture
- [ ] Add test audio file fixture
- [ ] Add Loguru capture fixture

**Implementation:**
```python
# tests/conftest.py
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, AsyncMock
from loguru import logger
import sys

from config import AlltalkConfig, AlltalkTTSEnginesConfig

@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests"""
    temp = tempfile.mkdtemp()
    yield Path(temp)
    shutil.rmtree(temp)

@pytest.fixture
def test_config(temp_dir):
    """Create test configuration"""
    config_path = temp_dir / "test_config.json"
    config = AlltalkConfig(config_path=config_path)
    config.branding = "TestAllTalk "
    config.gradio_interface = False
    config.launch_gradio = False
    config.save()
    return config

@pytest.fixture
def test_tts_engines_config(temp_dir):
    """Create test TTS engines configuration"""
    config_path = temp_dir / "test_tts_engines.json"
    config = AlltalkTTSEnginesConfig(config_path=config_path)
    config.engines_available = []
    config.engine_loaded = ""
    config.save()
    return config

@pytest.fixture
def mock_model_engine():
    """Create mock model engine"""
    engine = Mock()
    engine.engine_loaded = "test_engine"
    engine.current_model_loaded = "test_model"
    engine.available_models = {"test_model": {}}
    engine.multivoice_capable = True
    engine.deepspeed_capable = False
    engine.lowvram_capable = False
    engine.setup = AsyncMock()
    engine.unload_model = AsyncMock()
    engine.handle_tts_method_change = AsyncMock(return_value=True)
    return engine

@pytest.fixture
def test_audio_file(temp_dir):
    """Create test audio file"""
    audio_path = temp_dir / "test_audio.wav"
    # Create minimal WAV file
    import wave
    with wave.open(str(audio_path), 'w') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(22050)
        wav.writeframes(b'\x00\x00' * 1000)
    return audio_path

@pytest.fixture
def loguru_capture():
    """Capture Loguru output for testing"""
    from io import StringIO
    log_stream = StringIO()
    
    handler_id = logger.add(
        log_stream,
        format="{message}",
        level="DEBUG",
        serialize=False
    )
    
    yield log_stream
    
    logger.remove(handler_id)

@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset singleton instances between tests"""
    AlltalkConfig.__instance = None
    AlltalkTTSEnginesConfig.__instance = None
    yield
    AlltalkConfig.__instance = None
    AlltalkTTSEnginesConfig.__instance = None
```

**Testing:**
- Test all fixtures work correctly
- Test fixture cleanup works
- Test singleton reset works

---

### 5.3 Add Loguru Capture for Pytest
**File:** `tests/conftest.py`  
**Priority:** High  
**Effort:** 2 hours

**Tasks:**
- [ ] Install pytest-loguru plugin
- [ ] Configure log capture in conftest.py
- [ ] Add log assertion helpers

**Implementation:**
```python
# Add to conftest.py
from loguru import logger

@pytest.fixture
def log_capture():
    """Capture loguru logs for testing"""
    import io
    log_output = io.StringIO()
    
    handler_id = logger.add(
        log_output,
        format="{level} - {message}",
        level="DEBUG",
        serialize=False
    )
    
    class LogCapture:
        def get_logs(self):
            return log_output.getvalue()
        
        def assert_log_contains(self, text: str):
            assert text in log_output.getvalue(), f"Expected '{text}' in logs"
        
        def clear(self):
            log_output.truncate(0)
            log_output.seek(0)
    
    yield LogCapture()
    logger.remove(handler_id)
```

**Testing:**
- Test log capture works
- Test log assertions work

---

## Phase 6: Unit Tests (Week 3-4)

### 6.1 Write Tests for config.py
**File:** `tests/test_config.py` (already exists, needs expansion)  
**Priority:** High  
**Effort:** 12 hours

**Tasks:**
- [ ] Test AlltalkConfig initialization
- [ ] Test config file loading
- [ ] Test config file saving
- [ ] Test config hot-reload
- [ ] Test config validation
- [ ] Test singleton pattern
- [ ] Test file locking and backup

**Implementation:**
```python
# tests/test_config.py
import pytest
import json
from pathlib import Path
from config import AlltalkConfig, AlltalkTTSEnginesConfig, AlltalkConfigModel

class TestAlltalkConfig:
    def test_config_initialization(self, temp_dir):
        """Test config initializes with default values"""
        config_path = temp_dir / "config.json"
        config = AlltalkConfig(config_path=config_path)
        
        assert config.branding == "AllTalk "
        assert config.gradio_interface == True
        assert config.output_folder == "outputs"
    
    def test_config_save_and_load(self, temp_dir):
        """Test config saves and loads correctly"""
        config_path = temp_dir / "config.json"
        config = AlltalkConfig(config_path=config_path)
        config.branding = "TestBranding"
        config.save()
        
        # Load new instance
        config2 = AlltalkConfig(config_path=config_path)
        assert config2.branding == "TestBranding"
    
    def test_config_hot_reload(self, temp_dir):
        """Test config reloads on file change"""
        config_path = temp_dir / "config.json"
        config = AlltalkConfig(config_path=config_path, file_check_interval=1)
        
        # Modify file externally
        with open(config_path, 'w') as f:
            json.dump({"branding": "Reloaded"}, f)
        
        # Wait for reload
        import time
        time.sleep(2)
        config._reload_on_change()
        
        assert config.branding == "Reloaded"
    
    def test_config_validation(self, temp_dir):
        """Test config validates Pydantic models"""
        config_path = temp_dir / "config.json"
        
        # Write invalid config
        with open(config_path, 'w') as f:
            json.dump({"gradio_port_number": "invalid"}, f)
        
        with pytest.raises(Exception):
            AlltalkConfig(config_path=config_path)
    
    def test_singleton_pattern(self, temp_dir):
        """Test singleton pattern works"""
        config_path = temp_dir / "config.json"
        config1 = AlltalkConfig(config_path=config_path)
        config2 = AlltalkConfig.get_instance()
        
        # Should be same instance if path matches
        assert config1.get_config_path() == config2.get_config_path()

class TestAlltalkTTSEnginesConfig:
    def test_engine_validation(self, temp_dir):
        """Test engine validation"""
        config_path = temp_dir / "engines.json"
        config = AlltalkTTSEnginesConfig(config_path=config_path)
        config.engines_available = [
            {"name": "xtts", "selected_model": "model1"},
            {"name": "vits", "selected_model": "model2"}
        ]
        config.save()
        
        assert config.is_valid_engine("xtts") == True
        assert config.is_valid_engine("invalid") == False
    
    def test_engine_change(self, temp_dir):
        """Test engine change"""
        config_path = temp_dir / "engines.json"
        config = AlltalkTTSEnginesConfig(config_path=config_path)
        config.engines_available = [
            {"name": "xtts", "selected_model": "model1"},
            {"name": "vits", "selected_model": "model2"}
        ]
        config.engine_loaded = "xtts"
        config.save()
        
        config.change_engine("vits")
        assert config.engine_loaded == "vits"
        assert config.selected_model == "model2"
```

**Testing:**
- Run all config tests
- Achieve >90% coverage for config.py

---

### 6.2 Write Tests for tts_server.py API Endpoints
**File:** `tests/test_api_endpoints.py`  
**Priority:** High  
**Effort:** 16 hours

**Tasks:**
- [ ] Test /api/reload endpoint
- [ ] Test /api/enginereload endpoint
- [ ] Test /api/stop-generation endpoint
- [ ] Test /api/audio endpoint
- [ ] Test /api/voices endpoint
- [ ] Test /api/rvcvoices endpoint
- [ ] Test /api/reload_config endpoint
- [ ] Test /api/ready endpoint
- [ ] Test /api/currentsettings endpoint
- [ ] Test /api/lowvramsetting endpoint
- [ ] Test /api/deepspeed endpoint
- [ ] Test /api/voice2rvc endpoint

**Implementation:**
```python
# tests/test_api_endpoints.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
from tts_server import app

@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)

class TestReloadEndpoint:
    def test_reload_success(self, client, mock_model_engine):
        """Test successful model reload"""
        with patch('tts_server.model_engine', mock_model_engine):
            response = client.post("/api/reload?tts_method=test_model")
            assert response.status_code == 200
            assert response.json() == {"status": "model-success"}
    
    def test_reload_invalid_model(self, client, mock_model_engine):
        """Test reload with invalid model"""
        mock_model_engine.available_models = {"valid_model": {}}
        with patch('tts_server.model_engine', mock_model_engine):
            response = client.post("/api/reload?tts_method=invalid_model")
            assert response.status_code == 200
            assert response.json()["status"] == "error"

class TestVoicesEndpoint:
    def test_get_voices_success(self, client, mock_model_engine):
        """Test getting voices list"""
        mock_model_engine.multivoice_capable = True
        mock_model_engine.voices_file_list = Mock(return_value=["voice1.wav", "voice2.wav"])
        
        with patch('tts_server.model_engine', mock_model_engine):
            response = client.get("/api/voices")
            assert response.status_code == 200
            assert response.json()["status"] == "success"
            assert len(response.json()["voices"]) == 2
    
    def test_get_voices_not_supported(self, client, mock_model_engine):
        """Test voices when engine doesn't support it"""
        mock_model_engine.multivoice_capable = False
        
        with patch('tts_server.model_engine', mock_model_engine):
            response = client.get("/api/voices")
            assert response.status_code == 500
            assert "does not support multiple voices" in response.json()["message"]

class TestAudioEndpoint:
    def test_get_audio_success(self, client, test_audio_file):
        """Test getting audio file"""
        with patch('tts_server.config') as mock_config:
            mock_config.get_output_directory.return_value = test_audio_file.parent
            
            response = client.get(f"/audio/{test_audio_file.name}")
            assert response.status_code == 200
            assert response.headers["content-type"] == "audio/wav"
    
    def test_get_audio_not_found(self, client):
        """Test getting non-existent audio file"""
        with patch('tts_server.config') as mock_config:
            mock_config.get_output_directory.return_value = Path("/fake/path")
            
            response = client.get("/audio/nonexistent.wav")
            assert response.status_code == 404
```

**Testing:**
- Run all API endpoint tests
- Achieve >80% coverage for tts_server.py

---

### 6.3 Write Tests for TTS Engine Interfaces
**File:** `tests/test_tts_engines.py`  
**Priority:** Medium  
**Effort:** 12 hours

**Tasks:**
- [ ] Test XTTS engine interface
- [ ] Test VITS engine interface
- [ ] Test Piper engine interface
- [ ] Test engine loading/unloading
- [ ] Test model switching
- [ ] Test capability flags

**Implementation:**
```python
# tests/test_tts_engines.py
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

class TestXTTSEngine:
    @pytest.mark.gpu
    def test_xtts_setup(self):
        """Test XTTS engine setup (requires GPU)"""
        from system.tts_engines.xtts.model_engine import tts_class
        
        engine = tts_class()
        # Test setup logic
    
    def test_xtts_capabilities(self):
        """Test XTTS capability flags"""
        from system.tts_engines.xtts.model_engine import tts_class
        
        engine = tts_class()
        assert hasattr(engine, 'deepspeed_capable')
        assert hasattr(engine, 'lowvram_capable')
        assert hasattr(engine, 'multivoice_capable')

class TestPiperEngine:
    def test_piper_setup(self):
        """Test Piper engine setup"""
        from system.tts_engines.piper.model_engine import tts_class
        
        engine = tts_class()
        # Test setup logic

class TestEngineInterface:
    def test_all_engines_have_required_methods(self):
        """Test all engines implement required interface"""
        required_methods = [
            'setup',
            'unload_model',
            'handle_tts_method_change',
            'tts_generate',
            'voices_file_list'
        ]
        
        engines = ['xtts', 'vits', 'piper', 'parler', 'f5tts']
        
        for engine_name in engines:
            module = __import__(f'system.tts_engines.{engine_name}.model_engine', fromlist=['tts_class'])
            engine_class = getattr(module, 'tts_class')
            engine = engine_class()
            
            for method in required_methods:
                assert hasattr(engine, method), f"{engine_name} missing {method}"
```

**Testing:**
- Run all engine tests
- Mark GPU tests appropriately

---

### 6.4 Write Tests for RVC Pipeline
**File:** `tests/test_rvc.py`  
**Priority:** Medium  
**Effort:** 8 hours

**Tasks:**
- [ ] Test RVC inference pipeline
- [ ] Test RVC configuration
- [ ] Test voice conversion
- [ ] Test error handling

**Implementation:**
```python
# tests/test_rvc.py
import pytest
from pathlib import Path
from unittest.mock import Mock, patch

class TestRVCPipeline:
    def test_rvc_inference(self, test_audio_file, temp_dir):
        """Test RVC inference"""
        from system.tts_engines.rvc.infer.infer import infer_pipeline
        
        # Mock the pipeline for testing
        with patch('system.tts_engines.rvc.infer.infer.infer_pipeline') as mock_pipeline:
            mock_pipeline.return_value = str(temp_dir / "output.wav")
            
            result = infer_pipeline(
                pitch=0,
                filter_radius=3,
                index_rate=0.75,
                # ... other parameters
            )
            
            assert result == str(temp_dir / "output.wav")
    
    def test_rvc_error_handling(self, test_audio_file):
        """Test RVC error handling"""
        with pytest.raises(Exception):
            # Test with invalid parameters
            pass
```

**Testing:**
- Run all RVC tests
- Test error paths

---

### 6.5 Write Tests for Error Handling Paths
**File:** `tests/test_error_handling.py`  
**Priority:** Medium  
**Effort:** 8 hours

**Tasks:**
- [ ] Test custom exceptions
- [ ] Test error decorator
- [ ] Test error propagation
- [ ] Test error logging

**Implementation:**
```python
# tests/test_error_handling.py
import pytest
from system.exceptions import AllTalkError, ConfigurationError, TTSEngineError
from system.error_handler import handle_errors
from loguru import logger

class TestCustomExceptions:
    def test_configuration_error(self):
        """Test ConfigurationError"""
        with pytest.raises(ConfigurationError):
            raise ConfigurationError("Invalid config")
    
    def test_tts_engine_error(self):
        """Test TTSEngineError"""
        with pytest.raises(TTSEngineError):
            raise TTSEngineError("TTS failed")

class TestErrorDecorator:
    def test_decorator_catches_alltalk_errors(self, loguru_capture):
        """Test decorator catches AllTalk errors"""
        @handle_errors("TEST")
        async def failing_function():
            raise ConfigurationError("Test error")
        
        with pytest.raises(ConfigurationError):
            await failing_function()
        
        loguru_capture.assert_log_contains("ConfigurationError")
    
    def test_decorator_wraps_unexpected_errors(self, loguru_capture):
        """Test decorator wraps unexpected errors"""
        @handle_errors("TEST")
        async def failing_function():
            raise ValueError("Unexpected error")
        
        with pytest.raises(AllTalkError):
            await failing_function()
        
        loguru_capture.assert_log_contains("Unexpected error")
```

**Testing:**
- Run all error handling tests
- Verify logging works

---

### 6.6 Write Tests for File Operations and Config Reload
**File:** `tests/test_file_operations.py`  
**Priority:** Medium  
**Effort:** 8 hours

**Tasks:**
- [ ] Test config file backup
- [ ] Test file locking
- [ ] Test concurrent file access
- [ ] Test file cleanup

**Implementation:**
```python
# tests/test_file_operations.py
import pytest
import asyncio
from pathlib import Path
from config import AlltalkConfig

class TestFileOperations:
    def test_config_backup_on_save(self, temp_dir):
        """Test config creates backup on save"""
        config_path = temp_dir / "config.json"
        config = AlltalkConfig(config_path=config_path)
        config.save()
        
        backup_path = config_path.with_suffix('.backup')
        assert not backup_path.exists()  # Backup should be cleaned up
    
    def test_file_locking(self, temp_dir):
        """Test file locking prevents concurrent access"""
        config_path = temp_dir / "config.json"
        config1 = AlltalkConfig(config_path=config_path)
        config2 = AlltalkConfig(config_path=config_path)
        
        # Test that file locking works
        config1.save()
        config2.save()  # Should wait for lock
    
    @pytest.mark.asyncio
    async def test_concurrent_config_access(self, temp_dir):
        """Test concurrent config access"""
        config_path = temp_dir / "config.json"
        
        async def modify_config():
            config = AlltalkConfig(config_path=config_path)
            config.save()
        
        # Run multiple concurrent saves
        await asyncio.gather(*[modify_config() for _ in range(5)])
        
        # Verify config is still valid
        config = AlltalkConfig(config_path=config_path)
        assert config.branding == "AllTalk "
```

**Testing:**
- Run all file operation tests
- Test concurrent scenarios

---

## Phase 7: Integration Tests (Week 4)

### 7.1 Write Tests for API Integration
**File:** `tests/integration/test_api_integration.py`  
**Priority:** Medium  
**Effort:** 12 hours

**Tasks:**
- [ ] Test full TTS generation workflow via API
- [ ] Test model switching workflow
- [ ] Test RVC integration with TTS
- [ ] Test error recovery

**Implementation:**
```python
# tests/integration/test_api_integration.py
import pytest
from fastapi.testclient import TestClient
from tts_server import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.mark.integration
def test_full_tts_workflow(client, temp_dir):
    """Test complete TTS generation workflow"""
    # 1. Check if ready
    response = client.get("/api/ready")
    assert response.status_code == 200
    
    # 2. Get available voices
    response = client.get("/api/voices")
    assert response.status_code == 200
    
    # 3. Generate TTS
    response = client.post("/api/tts", json={
        "text": "Test text",
        "voice": "test_voice.wav"
    })
    assert response.status_code == 200
    
    # 4. Get audio
    audio_url = response.json()["output_file_url"]
    response = client.get(audio_url)
    assert response.status_code == 200
```

**Testing:**
- Run integration tests
- Test end-to-end workflows

---

### 7.2 Write Tests for TTS Generation Workflow
**File:** `tests/integration/test_tts_workflow.py`  
**Priority:** Medium  
**Effort:** 12 hours

**Tasks:**
- [ ] Test TTS generation with different engines
- [ ] Test audio output quality
- [ ] Test text preprocessing
- [ ] Test language detection

**Implementation:**
```python
# tests/integration/test_tts_workflow.py
import pytest
from pathlib import Path

@pytest.mark.integration
@pytest.mark.slow
def test_tts_generation_with_xtts(temp_dir):
    """Test TTS generation with XTTS engine"""
    # Load XTTS engine
    # Generate audio
    # Verify output
    pass

@pytest.mark.integration
@pytest.mark.slow
def test_text_preprocessing():
    """Test text preprocessing"""
    # Test various text inputs
    # Test filtering
    # Test language detection
    pass
```

**Testing:**
- Run integration tests
- Mark slow tests appropriately

---

## Phase 8: Documentation (Week 4-5)

### 8.1 Update Docstrings to Consistent Format
**Files:** Throughout codebase  
**Priority:** Low  
**Effort:** 16 hours

**Tasks:**
- [ ] Choose docstring format (Google style recommended)
- [ ] Update all public function docstrings
- [ ] Update all class docstrings
- [ ] Add parameter and return documentation
- [ ] Add raises documentation

**Implementation:**
```python
# Google style docstring example
def load_config(force_reload: bool = False) -> None:
    """Initialize all configuration instances.
    
    Loads the AlltalkConfig and AlltalkTTSEnginesConfig singletons.
    Optionally forces a reload of the configuration from disk.
    
    Args:
        force_reload: If True, forces a reload even if the file
            hasn't been modified. Defaults to False.
    
    Raises:
        ConfigurationError: If configuration file is invalid or
            cannot be loaded.
    
    Example:
        >>> load_config(force_reload=True)
        Configuration reloaded successfully
    """
    global config, tts_engines_config
    config = AlltalkConfig.get_instance(force_reload)
    tts_engines_config = AlltalkTTSEnginesConfig.get_instance(force_reload)
    after_config_load()
```

**Testing:**
- Use docstring formatter to enforce consistency
- Run documentation generation tools

---

### 8.2 Extract Magic Numbers to Named Constants
**Files:** Throughout codebase  
**Priority:** Low  
**Effort:** 8 hours

**Tasks:**
- [ ] Identify all magic numbers
- [ ] Create constants module
- [ ] Replace magic numbers with constants
- [ ] Document why specific values were chosen

**Implementation:**
```python
# Create system/constants.py
"""Constants for AllTalk TTS application"""

# Audio processing
SAMPLE_RATE_16K = 16000
SAMPLE_RATE_22K = 22050
SAMPLE_RATE_44K = 44100
SAMPLE_RATE_48K = 48000

# TTS generation
DEFAULT_MAX_TEXT_LENGTH = 2000
DEFAULT_PITCH = 0
DEFAULT_TEMPERATURE = 0.75

# RVC settings
DEFAULT_FILTER_RADIUS = 3
DEFAULT_INDEX_RATE = 0.75
DEFAULT_HOP_LENGTH = 128

# API
DEFAULT_API_PORT = 7851
DEFAULT_GRADIO_PORT = 7852
DEFAULT_TIMEOUT = 30

# File operations
MAX_FILE_SIZE_MB = 500
LOG_RETENTION_DAYS = 10

# Use in code
from system.constants import DEFAULT_API_PORT, DEFAULT_TIMEOUT

# Instead of:
# port = 7851
# timeout = 30

# Use:
port = DEFAULT_API_PORT
timeout = DEFAULT_TIMEOUT
```

**Testing:**
- Verify all constants are used correctly
- No behavior changes

---

### 8.3 Standardize Naming Conventions
**Files:** Throughout codebase  
**Priority:** Low  
**Effort:** 8 hours

**Tasks:**
- [ ] Audit naming conventions across codebase
- [ ] Rename variables to snake_case
- [ ] Rename functions to snake_case
- [ ] Ensure class names are PascalCase
- [ ] Update all imports and references

**Implementation:**
```python
# Before
def processAudioFile(inputPath):
    pass

# After
def process_audio_file(input_path: Path) -> None:
    pass
```

**Testing:**
- Run tests to ensure no breakage
- Update documentation

---

## Phase 9: CI/CD (Week 5)

### 9.1 Set Up Pytest in CI Pipeline
**File:** `.github/workflows/test.yml`  
**Priority:** Medium  
**Effort:** 4 hours

**Tasks:**
- [ ] Create GitHub Actions workflow
- [ ] Configure test execution on push/PR
- [ ] Add coverage reporting
- [ ] Add coverage badge to README

**Implementation:**
```yaml
# .github/workflows/test.yml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.9', '3.10', '3.11']
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r system/requirements/requirements_unit_test.txt
        pip install pytest pytest-asyncio pytest-cov pytest-loguru
    
    - name: Run tests
      run: |
        pytest --cov=. --cov-report=xml --cov-report=html
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

**Testing:**
- Test CI workflow runs successfully
- Verify coverage reports work

---

### 9.2 Add MyPy Type Checking to CI
**File:** `.github/workflows/test.yml`  
**Priority:** Medium  
**Effort:** 4 hours

**Tasks:**
- [ ] Add mypy to CI workflow
- [ ] Create mypy configuration
- [ ] Fix type errors incrementally

**Implementation:**
```yaml
# Add to test workflow
- name: Type checking with mypy
  run: |
    pip install mypy
    mypy . --ignore-missing-imports --no-strict-optional
```

```ini
# mypy.ini
[mypy]
python_version = 3.9
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = False  # Incrementally enable
ignore_missing_imports = True

[mypy-tests.*]
disallow_untyped_defs = False
```

**Testing:**
- Run mypy in CI
- Fix critical type errors

---

### 9.3 Add Pre-commit Hooks
**File:** `.pre-commit-config.yaml`  
**Priority:** Medium  
**Effort**: 4 hours

**Tasks:**
- [ ] Create pre-commit configuration
- [ ] Add hooks for linting, formatting, type checking
- [ ] Document pre-commit setup for developers

**Implementation:**
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3.9

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black"]

  - repo: https://github.com/PyCQA/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: ['--max-line-length=88', '--extend-ignore=E203']

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
        args: ['--ignore-missing-imports']
```

**Testing:**
- Test pre-commit hooks work
- Document setup for contributors

---

## Summary Timeline

| Week | Phase | Focus |
|------|-------|-------|
| 1 | Phase 1-2 | Critical security fixes, logging standardization |
| 2 | Phase 2-3 | Logging completion, error handling |
| 3 | Phase 4-5 | Code quality, testing infrastructure |
| 4 | Phase 5-6 | Unit tests completion |
| 5 | Phase 7-9 | Integration tests, documentation, CI/CD |

---

## Success Criteria

### Security
- [ ] CORS configured with specific origins
- [ ] No subprocess calls with shell=True on user input
- [ ] All user input validated and sanitized

### Code Quality
- [ ] No bare except clauses
- [ ] All print statements replaced with Loguru
- [ ] Type hints on all public APIs
- [ ] All files under 500 lines
- [ ] Pylint score >9.0/10

### Testing
- [ ] Unit test coverage >80%
- [ ] Integration tests for critical workflows
- [ ] All tests pass in CI
- [ ] Coverage reports generated

### Documentation
- [ ] Consistent docstring format
- [ ] No magic numbers
- [ ] Consistent naming conventions
- [ ] README updated with new standards

---

## Risk Mitigation

### Breaking Changes
- Maintain backward compatibility during refactoring
- Use feature flags for major changes
- Communicate changes to users

### Test Coverage
- Prioritize critical path testing
- Add tests before refactoring
- Use mutation testing for quality

### Resource Constraints
- Focus on high-priority issues first
- Split work into manageable chunks
- Use parallel development where possible

---

## Dependencies

### Required Packages
```
# Testing
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0
pytest-loguru>=0.2.0
pytest-mock>=3.11.0

# Logging
loguru>=0.7.0

# Type Checking
mypy>=1.3.0
types-all

# Code Quality
black>=23.3.0
isort>=5.12.0
flake8>=6.0.0
pylint>=2.17.0

# Pre-commit
pre-commit>=3.3.0
```

---

## Next Steps

1. **Immediate (Week 1):** Start with Phase 1 critical security fixes
2. **Short-term (Week 1-2):** Implement Loguru logging standardization
3. **Medium-term (Week 2-4):** Build testing infrastructure and write unit tests
4. **Long-term (Week 4-5):** Complete integration tests and CI/CD setup

---

**Plan Created:** 2025-04-21  
**Last Updated:** 2025-04-21  
**Owner:** Development Team  
**Review Date:** End of each phase
