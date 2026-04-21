# tests/test_config.py
import json
import time

import pytest

from config import AlltalkAvailableEngine, AlltalkConfig, AlltalkTTSEnginesConfig


class TestAlltalkConfig:
    def test_config_initialization(self, temp_dir):
        """Test config initializes with default values"""
        config_path = temp_dir / "config.json"
        # Create default config file
        with config_path.open("w") as f:
            json.dump({}, f)

        config = AlltalkConfig(config_path=config_path)

        assert config.branding == "AllTalk "
        assert config.gradio_interface is True
        assert config.output_folder == "outputs"

    def test_config_save_and_load(self, temp_dir):
        """Test config saves and loads correctly"""
        config_path = temp_dir / "config.json"
        # Create default config file
        with config_path.open("w") as f:
            json.dump({}, f)

        config = AlltalkConfig(config_path=config_path)
        config.branding = "TestBranding"
        config.save()

        # Load new instance
        config2 = AlltalkConfig(config_path=config_path)
        assert config2.branding == "TestBranding"

    def test_config_hot_reload(self, temp_dir):
        """Test config reloads on file change"""
        config_path = temp_dir / "config.json"
        # Create default config file
        with config_path.open("w") as f:
            json.dump({"branding": "Initial"}, f)

        config = AlltalkConfig(config_path=config_path)

        # Modify file externally
        with config_path.open("w") as f:
            json.dump({"branding": "Reloaded"}, f)

        # Wait for reload
        time.sleep(6)
        config._reload_on_change()

        assert config.branding == "Reloaded"

    def test_config_validation(self, temp_dir):
        """Test config validates Pydantic models"""
        config_path = temp_dir / "config.json"

        # Write invalid config
        with config_path.open("w") as f:
            json.dump({"gradio_port_number": "invalid"}, f)

        with pytest.raises(Exception, match="Failed to save config"):
            AlltalkConfig(config_path=config_path)

    def test_singleton_pattern(self):
        """Test singleton pattern works"""
        # Reset singleton for test
        AlltalkConfig._AlltalkConfig__instance = None

        config1 = AlltalkConfig.get_instance()
        config2 = AlltalkConfig.get_instance()

        # Should be same instance
        assert config1 is config2


class TestAlltalkTTSEnginesConfig:
    def test_engine_validation(self, temp_dir):
        """Test engine validation"""
        config_path = temp_dir / "engines.json"
        # Create default config file
        with config_path.open("w") as f:
            json.dump({}, f)

        config = AlltalkTTSEnginesConfig(config_path=config_path)
        config.engines_available = [
            AlltalkAvailableEngine(name="xtts", selected_model="model1"),
            AlltalkAvailableEngine(name="vits", selected_model="model2"),
        ]
        config.save()

        # Check if engines are in the list
        engine_names = [engine.name for engine in config.engines_available]
        assert "xtts" in engine_names
        assert "vits" in engine_names
        assert "invalid" not in engine_names

    def test_engine_change(self, temp_dir):
        """Test engine change"""
        config_path = temp_dir / "engines.json"
        # Create default config file
        with config_path.open("w") as f:
            json.dump({}, f)

        config = AlltalkTTSEnginesConfig(config_path=config_path)
        config.engines_available = [
            AlltalkAvailableEngine(name="xtts", selected_model="model1"),
            AlltalkAvailableEngine(name="vits", selected_model="model2"),
        ]
        config.engine_loaded = "xtts"
        config.save()

        config.change_engine("vits")
        assert config.engine_loaded == "vits"
        assert config.selected_model == "model2"
