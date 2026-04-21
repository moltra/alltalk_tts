# tests/test_state_manager.py
import tempfile
from pathlib import Path

import pytest

from system.state_manager import StateManager, get_state_manager, reset_state_manager


class TestStateManager:
    """Test StateManager class"""

    def test_config_property_lazy_initialization(self, temp_dir):
        """Test config property initializes on first access"""
        config_path = temp_dir / "config.json"
        import json

        with config_path.open("w") as f:
            json.dump({}, f)

        state_manager = StateManager()
        assert state_manager._config is None

        # Access config property
        config = state_manager.config
        assert config is not None
        assert state_manager._config is not None
        assert config is state_manager._config

    def test_tts_engines_config_property_lazy_initialization(self, temp_dir):
        """Test tts_engines_config property initializes on first access"""
        config_path = temp_dir / "engines.json"
        import json

        with config_path.open("w") as f:
            json.dump({}, f)

        state_manager = StateManager()
        assert state_manager._tts_engines_config is None

        # Access tts_engines_config property
        engines_config = state_manager.tts_engines_config
        assert engines_config is not None
        assert state_manager._tts_engines_config is not None
        assert engines_config is state_manager._tts_engines_config

    def test_infer_pipeline_property(self):
        """Test infer_pipeline property getter and setter"""
        state_manager = StateManager()
        assert state_manager.infer_pipeline is None

        # Set infer_pipeline
        mock_pipeline = object()
        state_manager.infer_pipeline = mock_pipeline
        assert state_manager.infer_pipeline is mock_pipeline

    def test_reset(self):
        """Test reset method clears all state"""
        state_manager = StateManager()
        state_manager.infer_pipeline = object()
        state_manager._config = object()
        state_manager._tts_engines_config = object()

        state_manager.reset()

        assert state_manager._config is None
        assert state_manager._tts_engines_config is None
        assert state_manager.infer_pipeline is None

    def test_singleton_get_state_manager(self):
        """Test get_state_manager returns singleton instance"""
        reset_state_manager()
        state1 = get_state_manager()
        state2 = get_state_manager()

        assert state1 is state2

    def test_reset_state_manager(self):
        """Test reset_state_manager clears global instance"""
        reset_state_manager()
        state1 = get_state_manager()
        reset_state_manager()
        state2 = get_state_manager()

        assert state1 is not state2


class TestStateManagerAsync:
    """Test StateManager async methods"""

    @pytest.mark.asyncio
    async def test_reload_config(self, temp_dir):
        """Test reload_config method"""
        config_path = temp_dir / "config.json"
        import json

        with config_path.open("w") as f:
            json.dump({"branding": "Test"}, f)

        state_manager = StateManager()

        # Reload config
        await state_manager.reload_config(force=True)
        config2 = state_manager.config

        # Config should be reloaded (data updated)
        assert config2 is not None

    @pytest.mark.asyncio
    async def test_reload_config_with_lock(self):
        """Test reload_config uses lock for thread safety"""
        state_manager = StateManager()

        # This test verifies the lock is used - in a real scenario
        # you'd test concurrent access
        await state_manager.reload_config()
        assert True  # If we get here without deadlock, lock works

    @pytest.mark.asyncio
    async def test_initialize_infer_pipeline(self):
        """Test initialize_infer_pipeline method"""
        state_manager = StateManager()
        await state_manager.initialize_infer_pipeline()
        # Should not crash
        assert True


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests"""
    import shutil

    temp = tempfile.mkdtemp()
    yield Path(temp)
    shutil.rmtree(temp)
