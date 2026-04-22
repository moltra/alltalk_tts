"""
Tests for XTTS Engine Implementation

Tests cover the core functionality of the XTTS engine including:
- Model scanning and loading
- Voice file detection
- Model switching
- Configuration management
"""

import json
import sys
from unittest.mock import AsyncMock, Mock, patch

import pytest

# Mock the imports that might not be available in test environment
sys_modules = [
    "torch",
    "torchaudio",
    "TTS",
    "TTS.api",
    "TTS.tts.configs.xtts_config",
    "TTS.tts.models.xtts",
    "TTS.utils.synthesizer",
    "deepspeed",
]

for module in sys_modules:
    if module not in sys.modules:
        mock = Mock()
        if module == "torch":
            mock.__version__ = "2.0.0"
        sys.modules[module] = mock


@pytest.fixture
def temp_xtts_dir(temp_dir):
    """Create temporary XTTS engine directory structure"""
    xtts_dir = temp_dir / "system" / "tts_engines" / "xtts"
    xtts_dir.mkdir(parents=True, exist_ok=True)

    # Create model_settings.json
    model_settings = {
        "model_details": {"manufacturer_name": "Coqui", "manufacturer_website": "https://coqui.ai"},
        "model_capabilties": {
            "audio_format": "wav",
            "deepspeed_capable": True,
            "generationspeed_capable": True,
            "languages_capable": True,
            "lowvram_capable": True,
            "multimodel_capable": True,
            "repetitionpenalty_capable": True,
            "streaming_capable": True,
            "temperature_capable": True,
            "multivoice_capable": True,
            "pitch_capable": False,
        },
        "settings": {
            "def_character_voice": "female_01.wav",
            "def_narrator_voice": "female_01.wav",
            "deepspeed_enabled": False,
            "engine_installed": True,
            "generationspeed_set": 1.0,
            "lowvram_enabled": False,
            "repetitionpenalty_set": 7.0,
            "temperature_set": 0.75,
            "pitch_set": 0,
        },
        "openai_voices": {
            "alloy": "female_01.wav",
            "echo": "male_01.wav",
            "fable": "female_02.wav",
            "nova": "female_01.wav",
            "onyx": "male_02.wav",
            "shimmer": "female_03.wav",
        },
    }

    (xtts_dir / "model_settings.json").write_text(json.dumps(model_settings))

    return xtts_dir


@pytest.fixture
def temp_models_dir(temp_dir):
    """Create temporary models directory for testing"""
    models_dir = temp_dir / "models" / "xtts"
    models_dir.mkdir(parents=True, exist_ok=True)
    return models_dir


@pytest.fixture
def temp_voices_dir(temp_dir):
    """Create temporary voices directory for testing"""
    voices_dir = temp_dir / "voices"
    voices_dir.mkdir(parents=True, exist_ok=True)
    return voices_dir


class TestXTTSScanModelsFolder:
    """Tests for scan_models_folder function"""

    def test_scan_empty_models_folder(self, temp_models_dir, temp_xtts_dir, temp_dir):
        """Test scanning an empty models folder"""
        # Create a minimal valid model folder with all required files
        model_folder = temp_models_dir / "test_model"
        model_folder.mkdir()

        required_files = ["config.json", "model.pth", "mel_stats.pth", "speakers_xtts.pth", "vocab.json", "dvae.pth"]

        for file in required_files:
            (model_folder / file).write_text("{}")

        # Mock the necessary config classes
        with (
            patch("config.AlltalkConfig"),
            patch("config.AlltalkTTSEnginesConfig"),
            patch("config.AlltalkNewEnginesConfig"),
        ):
            from system.tts_engines.xtts.model_engine import tts_class

            engine = tts_class()
            engine.main_dir = temp_dir
            engine.model_folder_name = "xtts"

            available_models = engine.scan_models_folder()

            assert "xtts - test_model" in available_models
            assert "apitts - test_model" in available_models

    def test_scan_models_missing_required_files(self, temp_models_dir, temp_xtts_dir, temp_dir):
        """Test scanning models folder with incomplete model"""
        model_folder = temp_models_dir / "incomplete_model"
        model_folder.mkdir()

        # Only create some files, not all required
        (model_folder / "config.json").write_text("{}")
        (model_folder / "model.pth").write_text("{}")

        with (
            patch("config.AlltalkConfig"),
            patch("config.AlltalkTTSEnginesConfig"),
            patch("config.AlltalkNewEnginesConfig"),
        ):
            from system.tts_engines.xtts.model_engine import tts_class

            engine = tts_class()
            engine.main_dir = temp_dir
            engine.model_folder_name = "xtts"

            available_models = engine.scan_models_folder()

            # Should return "No Models Available" when no valid models found
            assert "No Models Available" in available_models

    def test_scan_multiple_valid_models(self, temp_models_dir, temp_xtts_dir, temp_dir):
        """Test scanning with multiple valid models"""
        required_files = ["config.json", "model.pth", "mel_stats.pth", "speakers_xtts.pth", "vocab.json", "dvae.pth"]

        for model_name in ["model1", "model2", "model3"]:
            model_folder = temp_models_dir / model_name
            model_folder.mkdir()
            for file in required_files:
                (model_folder / file).write_text("{}")

        with (
            patch("config.AlltalkConfig"),
            patch("config.AlltalkTTSEnginesConfig"),
            patch("config.AlltalkNewEnginesConfig"),
        ):
            from system.tts_engines.xtts.model_engine import tts_class

            engine = tts_class()
            engine.main_dir = temp_dir
            engine.model_folder_name = "xtts"

            available_models = engine.scan_models_folder()

            assert "xtts - model1" in available_models
            assert "xtts - model2" in available_models
            assert "xtts - model3" in available_models
            assert "apitts - model1" in available_models
            assert "apitts - model2" in available_models
            assert "apitts - model3" in available_models


class TestXTTSVoicesFileList:
    """Tests for voices_file_list function"""

    def test_voices_list_individual_wav_files(self, temp_voices_dir, temp_xtts_dir, temp_dir):
        """Test listing individual WAV voice files"""
        # Create some WAV files
        (temp_voices_dir / "voice1.wav").write_bytes(b"RIFF" + b"\x00" * 100)
        (temp_voices_dir / "voice2.wav").write_bytes(b"RIFF" + b"\x00" * 100)
        (temp_voices_dir / "not_a_voice.txt").write_text("text")

        with (
            patch("config.AlltalkConfig"),
            patch("config.AlltalkTTSEnginesConfig"),
            patch("config.AlltalkNewEnginesConfig"),
        ):
            from system.tts_engines.xtts.model_engine import tts_class

            engine = tts_class()
            engine.main_dir = temp_dir
            engine.current_model_loaded = "xtts - test_model"

            voices = engine.voices_file_list()

            assert "voice1.wav" in voices
            assert "voice2.wav" in voices
            assert "not_a_voice.txt" not in voices

    def test_voices_list_voice_sets(self, temp_voices_dir, temp_xtts_dir, temp_dir):
        """Test listing voice sets from multi_voice_sets directory"""
        multi_voice_dir = temp_voices_dir / "xtts_multi_voice_sets"
        multi_voice_dir.mkdir()

        # Create a voice set with multiple WAV files
        voice_set = multi_voice_dir / "voice_set_1"
        voice_set.mkdir()
        (voice_set / "sample1.wav").write_bytes(b"RIFF" + b"\x00" * 100)
        (voice_set / "sample2.wav").write_bytes(b"RIFF" + b"\x00" * 100)

        with (
            patch("config.AlltalkConfig"),
            patch("config.AlltalkTTSEnginesConfig"),
            patch("config.AlltalkNewEnginesConfig"),
        ):
            from system.tts_engines.xtts.model_engine import tts_class

            engine = tts_class()
            engine.main_dir = temp_dir
            engine.current_model_loaded = "xtts - test_model"

            voices = engine.voices_file_list()

            assert "voiceset:voice_set_1" in voices

    def test_voices_list_latents(self, temp_voices_dir, temp_xtts_dir, temp_dir):
        """Test listing latent JSON files"""
        latents_dir = temp_voices_dir / "xtts_latents"
        latents_dir.mkdir()

        (latents_dir / "latent1.json").write_text("{}")
        (latents_dir / "latent2.json").write_text("{}")

        with (
            patch("config.AlltalkConfig"),
            patch("config.AlltalkTTSEnginesConfig"),
            patch("config.AlltalkNewEnginesConfig"),
        ):
            from system.tts_engines.xtts.model_engine import tts_class

            engine = tts_class()
            engine.main_dir = temp_dir
            engine.current_model_loaded = "xtts - test_model"

            voices = engine.voices_file_list()

            assert "latent:latent1.json" in voices
            assert "latent:latent2.json" in voices

    def test_voices_list_no_voices_found(self, temp_voices_dir, temp_xtts_dir, temp_dir):
        """Test when no voices are available"""
        with (
            patch("config.AlltalkConfig"),
            patch("config.AlltalkTTSEnginesConfig"),
            patch("config.AlltalkNewEnginesConfig"),
        ):
            from system.tts_engines.xtts.model_engine import tts_class

            engine = tts_class()
            engine.main_dir = temp_dir
            engine.current_model_loaded = "xtts - test_model"

            voices = engine.voices_file_list()

            assert voices == ["No Voices Found"]

    def test_voices_list_apitts_no_latents(self, temp_voices_dir, temp_xtts_dir, temp_dir):
        """Test that API TTS mode doesn't include latents"""
        latents_dir = temp_voices_dir / "xtts_latents"
        latents_dir.mkdir()
        (latents_dir / "latent1.json").write_text("{}")

        with (
            patch("config.AlltalkConfig"),
            patch("config.AlltalkTTSEnginesConfig"),
            patch("config.AlltalkNewEnginesConfig"),
        ):
            from system.tts_engines.xtts.model_engine import tts_class

            engine = tts_class()
            engine.main_dir = temp_dir
            engine.current_model_loaded = "apitts - test_model"

            voices = engine.voices_file_list()

            # API TTS should not include latents
            assert "latent:latent1.json" not in voices


class TestXTTSHandleTTSMethodChange:
    """Tests for handle_tts_method_change function"""

    @pytest.mark.asyncio
    async def test_handle_xtts_method_change(self, temp_xtts_dir, temp_models_dir, temp_dir):
        """Test switching to XTTS local model"""
        # Create a valid model
        model_folder = temp_models_dir / "test_model"
        model_folder.mkdir()
        required_files = ["config.json", "model.pth", "mel_stats.pth", "speakers_xtts.pth", "vocab.json", "dvae.pth"]
        for file in required_files:
            (model_folder / file).write_text("{}")

        with (
            patch("config.AlltalkConfig"),
            patch("config.AlltalkTTSEnginesConfig"),
            patch("config.AlltalkNewEnginesConfig"),
        ):
            from system.tts_engines.xtts.model_engine import tts_class

            engine = tts_class()
            engine.main_dir = temp_dir
            engine.model_folder_name = "xtts"
            engine.available_models = engine.scan_models_folder()

            # Mock the load functions
            engine.xtts_manual_load_model = AsyncMock(return_value=Mock())
            engine.unload_model = AsyncMock()

            result = await engine.handle_tts_method_change("xtts - test_model")

            assert result is True
            assert engine.current_model_loaded == "xtts - test_model"
            engine.unload_model.assert_called_once()
            engine.xtts_manual_load_model.assert_called_once_with("test_model")

    @pytest.mark.asyncio
    async def test_handle_apitts_method_change(self, temp_xtts_dir, temp_models_dir, temp_dir):
        """Test switching to API TTS model"""
        model_folder = temp_models_dir / "test_model"
        model_folder.mkdir()
        required_files = ["config.json", "model.pth", "mel_stats.pth", "speakers_xtts.pth", "vocab.json", "dvae.pth"]
        for file in required_files:
            (model_folder / file).write_text("{}")

        with (
            patch("config.AlltalkConfig"),
            patch("config.AlltalkTTSEnginesConfig"),
            patch("config.AlltalkNewEnginesConfig"),
        ):
            from system.tts_engines.xtts.model_engine import tts_class

            engine = tts_class()
            engine.main_dir = temp_dir
            engine.model_folder_name = "xtts"
            engine.available_models = engine.scan_models_folder()

            # Mock the load functions
            engine.load_model = AsyncMock(return_value=Mock())
            engine.unload_model = AsyncMock()

            result = await engine.handle_tts_method_change("apitts - test_model")

            assert result is True
            assert engine.current_model_loaded == "apitts - test_model"
            engine.unload_model.assert_called_once()
            engine.load_model.assert_called_once_with("test_model")

    @pytest.mark.asyncio
    async def test_handle_invalid_method(self, temp_xtts_dir, temp_dir):
        """Test handling invalid model type"""
        with (
            patch("config.AlltalkConfig"),
            patch("config.AlltalkTTSEnginesConfig"),
            patch("config.AlltalkNewEnginesConfig"),
        ):
            from system.tts_engines.xtts.model_engine import tts_class

            engine = tts_class()
            engine.available_models = {"test": "xtts"}

            result = await engine.handle_tts_method_change("invalid_type - model")

            assert result is False
            assert engine.current_model_loaded is None


class TestXTTSInitMethods:
    """Tests for __init__ helper methods"""

    def test_init_system_variables(self, temp_xtts_dir, temp_dir):
        """Test initialization of core system variables"""
        with (
            patch("config.AlltalkConfig"),
            patch("config.AlltalkTTSEnginesConfig"),
            patch("config.AlltalkNewEnginesConfig"),
        ):
            from system.tts_engines.xtts.model_engine import tts_class

            engine = tts_class()
            engine._init_system_variables()

            assert engine.this_dir is not None
            assert engine.main_dir is not None
            assert engine.device in ["cuda", "cpu"]
            assert engine.tts_generating_lock is False
            assert engine.tts_stop_generation is False
            assert engine.model is None
            assert engine.is_tts_model_loaded is False
            assert engine.current_model_loaded is None
            assert engine.available_models is None
            assert engine.setup_has_run is False

    def test_load_configuration(self, temp_xtts_dir, temp_dir):
        """Test loading model_settings.json configuration"""
        with (
            patch("config.AlltalkConfig"),
            patch("config.AlltalkTTSEnginesConfig"),
            patch("config.AlltalkNewEnginesConfig"),
        ):
            from system.tts_engines.xtts.model_engine import tts_class

            engine = tts_class()
            engine.main_dir = temp_dir
            engine.this_dir = temp_xtts_dir

            config = engine._load_configuration()

            assert isinstance(config, dict)
            assert "model_details" in config
            assert "model_capabilties" in config
            assert "settings" in config
            assert "openai_voices" in config

    def test_setup_model_details(self, temp_xtts_dir, temp_dir):
        """Test setting model details from configuration"""
        with (
            patch("config.AlltalkConfig"),
            patch("config.AlltalkTTSEnginesConfig"),
            patch("config.AlltalkNewEnginesConfig"),
        ):
            from system.tts_engines.xtts.model_engine import tts_class

            engine = tts_class()
            model_settings = {
                "model_details": {
                    "manufacturer_name": "Test Manufacturer",
                    "manufacturer_website": "https://test.com",
                }
            }

            engine._setup_model_details(model_settings)

            assert engine.manufacturer_name == "Test Manufacturer"
            assert engine.manufacturer_website == "https://test.com"

    def test_setup_capabilities(self, temp_xtts_dir, temp_dir):
        """Test setting capability flags from configuration"""
        with (
            patch("config.AlltalkConfig"),
            patch("config.AlltalkTTSEnginesConfig"),
            patch("config.AlltalkNewEnginesConfig"),
        ):
            from system.tts_engines.xtts.model_engine import tts_class

            engine = tts_class()
            model_settings = {
                "model_capabilties": {
                    "audio_format": "wav",
                    "deepspeed_capable": True,
                    "generationspeed_capable": True,
                    "languages_capable": True,
                    "lowvram_capable": True,
                    "multimodel_capable": True,
                    "repetitionpenalty_capable": True,
                    "streaming_capable": True,
                    "temperature_capable": True,
                    "multivoice_capable": True,
                    "pitch_capable": False,
                }
            }

            engine._setup_capabilities(model_settings)

            assert engine.audio_format == "wav"
            assert engine.deepspeed_capable is True
            assert engine.generationspeed_capable is True
            assert engine.languages_capable is True
            assert engine.lowvram_capable is True
            assert engine.multimodel_capable is True
            assert engine.repetitionpenalty_capable is True
            assert engine.streaming_capable is True
            assert engine.temperature_capable is True
            assert engine.multivoice_capable is True
            assert engine.pitch_capable is False

    def test_setup_engine_settings(self, temp_xtts_dir, temp_dir):
        """Test setting engine settings from configuration"""
        with (
            patch("config.AlltalkConfig"),
            patch("config.AlltalkTTSEnginesConfig"),
            patch("config.AlltalkNewEnginesConfig"),
        ):
            from system.tts_engines.xtts.model_engine import tts_class

            engine = tts_class()
            model_settings = {
                "settings": {
                    "def_character_voice": "test_voice",
                    "def_narrator_voice": "test_narrator",
                    "deepspeed_enabled": False,
                    "engine_installed": True,
                    "generationspeed_set": 1.0,
                    "lowvram_enabled": False,
                    "repetitionpenalty_set": 7.0,
                    "temperature_set": 0.75,
                    "pitch_set": 1.0,
                }
            }

            engine._setup_engine_settings(model_settings)

            assert engine.def_character_voice == "test_voice"
            assert engine.def_narrator_voice == "test_narrator"
            assert engine.deepspeed_enabled is False
            assert engine.engine_installed is True
            assert engine.generationspeed_set == 1.0
            assert engine.lowvram_enabled is False
            assert engine.repetitionpenalty_set == 7.0
            assert engine.temperature_set == 0.75
            assert engine.pitch_set == 1.0

    def test_setup_openai_mappings(self, temp_xtts_dir, temp_dir):
        """Test setting OpenAI voice mappings from configuration"""
        with (
            patch("config.AlltalkConfig"),
            patch("config.AlltalkTTSEnginesConfig"),
            patch("config.AlltalkNewEnginesConfig"),
        ):
            from system.tts_engines.xtts.model_engine import tts_class

            engine = tts_class()
            model_settings = {
                "openai_voices": {
                    "alloy": "alloy_voice",
                    "echo": "echo_voice",
                    "fable": "fable_voice",
                    "nova": "nova_voice",
                    "onyx": "onyx_voice",
                    "shimmer": "shimmer_voice",
                }
            }

            engine._setup_openai_mappings(model_settings)

            assert engine.openai_alloy == "alloy_voice"
            assert engine.openai_echo == "echo_voice"
            assert engine.openai_fable == "fable_voice"
            assert engine.openai_nova == "nova_voice"
            assert engine.openai_onyx == "onyx_voice"
            assert engine.openai_shimmer == "shimmer_voice"
