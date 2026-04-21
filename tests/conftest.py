# tests/conftest.py
import shutil
import tempfile
from io import StringIO
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest
from loguru import logger

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

    with wave.open(str(audio_path), "w") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(22050)
        wav.writeframes(b"\x00\x00" * 1000)
    return audio_path


@pytest.fixture
def loguru_capture():
    """Capture Loguru output for testing with assertion helpers"""
    log_stream = StringIO()

    handler_id = logger.add(log_stream, format="{level} - {message}", level="DEBUG", serialize=False)

    class LogCapture:
        """Helper class for log assertions"""

        def get_logs(self):
            """Get all captured logs"""
            return log_stream.getvalue()

        def assert_log_contains(self, text: str):
            """Assert that logs contain specific text"""
            assert text in log_stream.getvalue(), f"Expected '{text}' in logs"

        def assert_log_level(self, level: str):
            """Assert that logs contain a specific level"""
            assert level in log_stream.getvalue(), f"Expected '{level}' in logs"

        def clear(self):
            """Clear captured logs"""
            log_stream.truncate(0)
            log_stream.seek(0)

    yield LogCapture()
    logger.remove(handler_id)


@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset singleton instances between tests"""
    AlltalkConfig.__instance = None
    AlltalkTTSEnginesConfig.__instance = None
    yield
    AlltalkConfig.__instance = None
    AlltalkTTSEnginesConfig.__instance = None
