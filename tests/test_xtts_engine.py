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


class TestXTTSHelperMethods:
    """Tests for helper methods extracted from generate_tts"""

    def test_validate_generation_inputs_no_model(self, temp_xtts_dir, temp_dir):
        """Test validation when no model is loaded"""
        with (
            patch("config.AlltalkConfig"),
            patch("config.AlltalkTTSEnginesConfig"),
            patch("config.AlltalkNewEnginesConfig"),
        ):
            from system.tts_engines.xtts.model_engine import tts_class
            from fastapi import HTTPException

            engine = tts_class()
            engine.main_dir = temp_dir
            engine.is_tts_model_loaded = False

            with pytest.raises(HTTPException) as exc_info:
                engine._validate_generation_inputs()

            assert "tts model loaded" in str(exc_info.value.detail).lower()

    def test_validate_generation_inputs_model_loaded(self, temp_xtts_dir, temp_dir):
        """Test validation when model is loaded (should pass)"""
        with (
            patch("config.AlltalkConfig"),
            patch("config.AlltalkTTSEnginesConfig"),
            patch("config.AlltalkNewEnginesConfig"),
        ):
            from system.tts_engines.xtts.model_engine import tts_class

            engine = tts_class()
            engine.main_dir = temp_dir
            engine.is_tts_model_loaded = True

            # Should not raise any exception
            engine._validate_generation_inputs()

    def test_prepare_voice_input_single_wav(self, temp_voices_dir, temp_xtts_dir, temp_dir):
        """Test voice input preparation for single WAV file"""
        # Create a test WAV file
        (temp_voices_dir / "test_voice.wav").write_bytes(b"RIFF" + b"\x00" * 100)

        with (
            patch("config.AlltalkConfig"),
            patch("config.AlltalkTTSEnginesConfig"),
            patch("config.AlltalkNewEnginesConfig"),
        ):
            from system.tts_engines.xtts.model_engine import tts_class

            engine = tts_class()
            engine.main_dir = temp_dir
            engine.current_model_loaded = "xtts - test_model"
            engine._generate_conditioning_latents = Mock(return_value=(Mock(), Mock()))

            wavs_files, _gpt_cond_latent, _speaker_embedding = engine._prepare_voice_input("test_voice.wav")

            assert len(wavs_files) == 1
            assert "test_voice.wav" in wavs_files[0]
            engine._generate_conditioning_latents.assert_called_once()

    def test_prepare_voice_input_latent(self, temp_voices_dir, temp_xtts_dir, temp_dir):
        """Test voice input preparation for latent file"""
        latents_dir = temp_voices_dir / "xtts_latents"
        latents_dir.mkdir()
        (latents_dir / "test_latent.json").write_text("{}")

        with (
            patch("config.AlltalkConfig"),
            patch("config.AlltalkTTSEnginesConfig"),
            patch("config.AlltalkNewEnginesConfig"),
        ):
            from system.tts_engines.xtts.model_engine import tts_class

            engine = tts_class()
            engine.main_dir = temp_dir
            engine.current_model_loaded = "xtts - test_model"
            engine._load_latents = Mock(return_value=(Mock(), Mock()))

            wavs_files, _gpt_cond_latent, _speaker_embedding = engine._prepare_voice_input("latent:test_latent.json")

            assert len(wavs_files) == 0
            engine._load_latents.assert_called_once_with("latent:test_latent.json")

    def test_prepare_voice_input_voiceset(self, temp_voices_dir, temp_xtts_dir, temp_dir):
        """Test voice input preparation for voice set"""
        multi_voice_dir = temp_voices_dir / "xtts_multi_voice_sets"
        voice_set = multi_voice_dir / "test_set"
        voice_set.mkdir(parents=True)
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
            engine._generate_conditioning_latents = Mock(return_value=(Mock(), Mock()))

            wavs_files, _gpt_cond_latent, _speaker_embedding = engine._prepare_voice_input("voiceset:test_set")

            assert len(wavs_files) == 2
            engine._generate_conditioning_latents.assert_called_once()

    def test_prepare_voice_input_voiceset_empty(self, temp_voices_dir, temp_xtts_dir, temp_dir):
        """Test voice input preparation for empty voice set"""
        multi_voice_dir = temp_voices_dir / "xtts_multi_voice_sets"
        voice_set = multi_voice_dir / "empty_set"
        voice_set.mkdir(parents=True)

        with (
            patch("config.AlltalkConfig"),
            patch("config.AlltalkTTSEnginesConfig"),
            patch("config.AlltalkNewEnginesConfig"),
        ):
            from system.tts_engines.xtts.model_engine import tts_class
            from fastapi import HTTPException

            engine = tts_class()
            engine.main_dir = temp_dir
            engine.current_model_loaded = "xtts - test_model"

            with pytest.raises(HTTPException) as exc_info:
                engine._prepare_voice_input("voiceset:empty_set")

            assert "No WAV files found" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_cleanup_after_generation(self, temp_xtts_dir, temp_dir):
        """Test cleanup after generation"""
        with (
            patch("config.AlltalkConfig"),
            patch("config.AlltalkTTSEnginesConfig"),
            patch("config.AlltalkNewEnginesConfig"),
        ):
            from system.tts_engines.xtts.model_engine import tts_class

            engine = tts_class()
            engine.main_dir = temp_dir
            engine.lowvram_enabled = False
            engine.device = "cpu"
            engine.tts_generating_lock = True
            engine.deepspeed_enabled = False

            start_time = 0.0
            await engine._cleanup_after_generation(start_time)

            assert engine.tts_generating_lock is False

    def test_generate_non_streaming(self, temp_xtts_dir, temp_dir):
        """Test non-streaming audio generation"""
        with (
            patch("config.AlltalkConfig"),
            patch("config.AlltalkTTSEnginesConfig"),
            patch("config.AlltalkNewEnginesConfig"),
        ):
            from system.tts_engines.xtts.model_engine import tts_class

            engine = tts_class()
            engine.main_dir = temp_dir
            engine.model = Mock()
            engine.model.inference = Mock(return_value={"wav": Mock()})
            with patch("torchaudio.save") as mock_save:
                common_args = {"text": "test", "language": "en"}
                output_file = temp_dir / "output.wav"

                engine._generate_non_streaming(common_args, output_file)

                engine.model.inference.assert_called_once_with(**common_args)
                mock_save.assert_called_once()

    def test_generate_api_tts_normal(self, temp_voices_dir, temp_xtts_dir, temp_dir):
        """Test API TTS generation with normal voice file"""
        (temp_voices_dir / "test.wav").write_bytes(b"RIFF" + b"\x00" * 100)

        with (
            patch("config.AlltalkConfig"),
            patch("config.AlltalkTTSEnginesConfig"),
            patch("config.AlltalkNewEnginesConfig"),
        ):
            from system.tts_engines.xtts.model_engine import tts_class

            engine = tts_class()
            engine.main_dir = temp_dir
            engine.model = Mock()
            engine.model.config.length_penalty = 1.0
            engine.model.config.top_k = 50
            engine.model.config.top_p = 0.9
            engine.model.tts_to_file = Mock()

            output_file = temp_dir / "output.wav"
            engine._generate_api_tts(
                text="test text",
                voice="test.wav",
                wavs_files=[str(temp_voices_dir / "test.wav")],
                language="en",
                temperature=0.75,
                repetition_penalty=7.0,
                speed=1.0,
                output_file=output_file,
            )

            engine.model.tts_to_file.assert_called_once()
            call_args = engine.model.tts_to_file.call_args
            assert call_args[1]["text"] == "test text"
            assert "speaker_wav" in call_args[1]

    def test_generate_api_tts_latent_error(self, temp_voices_dir, temp_xtts_dir, temp_dir):
        """Test API TTS generation with latent file (should show error)"""
        with (
            patch("config.AlltalkConfig"),
            patch("config.AlltalkTTSEnginesConfig"),
            patch("config.AlltalkNewEnginesConfig"),
        ):
            from system.tts_engines.xtts.model_engine import tts_class

            engine = tts_class()
            engine.main_dir = temp_dir
            engine.model = Mock()
            engine.model.config.length_penalty = 1.0
            engine.model.config.top_k = 50
            engine.model.config.top_p = 0.9
            engine.model.tts_to_file = Mock()

            output_file = temp_dir / "output.wav"
            engine._generate_api_tts(
                text="test text",
                voice="latent:test.json",
                wavs_files=[],
                language="en",
                temperature=0.75,
                repetition_penalty=7.0,
                speed=1.0,
                output_file=output_file,
            )

            engine.model.tts_to_file.assert_called_once()
            call_args = engine.model.tts_to_file.call_args
            assert "API TTS method only supports audio files" in call_args[1]["text"]
            assert call_args[1]["speaker"] == "Ana Florence"

    @pytest.mark.asyncio
    async def test_generate_streaming(self, temp_xtts_dir, temp_dir):
        """Test streaming audio generation - verifies function call and WAV header"""
        with (
            patch("config.AlltalkConfig"),
            patch("config.AlltalkTTSEnginesConfig"),
            patch("config.AlltalkNewEnginesConfig"),
            patch("system.tts_engines.xtts.model_engine.torch"),
            patch("system.tts_engines.xtts.model_engine.np"),
        ):
            from system.tts_engines.xtts.model_engine import tts_class

            engine = tts_class()
            engine.main_dir = temp_dir
            engine.model = Mock()
            engine.tts_stop_generation = False

            # Mock the streaming generator to return empty (no audio chunks)
            engine.model.inference_stream = Mock(return_value=iter([]))

            common_args = {"text": "test", "language": "en"}
            wavs_files = ["test.wav"]

            chunks = []
            async for chunk in engine._generate_streaming(common_args, wavs_files):
                chunks.append(chunk)

            engine.model.inference_stream.assert_called_once_with(**common_args, stream_chunk_size=20)
            assert len(chunks) == 1  # Should yield just the WAV header
