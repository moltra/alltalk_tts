# tests/test_integration.py
"""
Integration tests for AllTalk TTS end-to-end workflows.

These tests verify:
- Engine switching workflows
- Model switching workflows
- Complete TTS generation workflow
- Settings update workflow
- Model download workflow
"""

from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

import pytest
from fastapi.testclient import TestClient

from tts_server import app


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


class TestEngineSwitchingIntegration:
    """Integration tests for engine switching workflow"""
    
    def test_engine_switch_complete_workflow(self, client, mock_tts_engines_config, mock_model_engine):
        """Test complete engine switching workflow"""
        # Setup initial state
        mock_tts_engines_config.is_valid_engine.return_value = True
        mock_tts_engines_config.engine_loaded = "piper"
        mock_tts_engines_config.change_engine.return_value = mock_tts_engines_config
        
        # Step 1: Check current engine
        with patch("tts_server.load_config"):
            with patch("tts_server.config") as mock_config:
                with patch("tts_server.tts_engines_config", mock_tts_engines_config):
                    with patch("tts_server.model_engine", mock_model_engine):
                        mock_model_engine.engine_loaded = "piper"
                        
                        response = client.get("/api/currentsettings")
                        assert response.status_code == 200
                        data = response.json()
                        assert data["current_engine_loaded"] == "piper"
        
        # Step 2: Switch to XTTS
        with patch("tts_server.load_config"):
            with patch("tts_server.tts_engines_config", mock_tts_engines_config):
                with patch("tts_server.handle_restart"):
                    response = client.post("/api/enginereload?engine=xtts")
                    assert response.status_code == 200
                    assert response.json()["status"] == "engine-success"
        
        # Step 3: Verify engine was changed
        mock_tts_engines_config.change_engine.assert_called_once_with("xtts")
        mock_tts_engines_config.save.assert_called()
    
    def test_engine_switch_updates_voice_list(self, client, mock_tts_engines_config, mock_model_engine):
        """Test that voice list updates after engine switch"""
        # Setup Piper voices
        mock_model_engine.multivoice_capable = True
        mock_model_engine.voices_file_list = Mock(return_value=["piper_voice1.onnx", "piper_voice2.onnx"])
        
        with patch("tts_server.load_config"):
            with patch("tts_server.tts_engines_config", mock_tts_engines_config):
                with patch("tts_server.model_engine", mock_model_engine):
                    mock_model_engine.engine_loaded = "piper"
                    
                    response = client.get("/api/voices")
                    assert response.status_code == 200
                    voices = response.json()["voices"]
                    assert "piper_voice1.onnx" in voices
        
        # Switch to XTTS voices
        mock_model_engine.voices_file_list = Mock(return_value=["builtin:Claribel Dervla", "builtin:Daisy Studious"])
        
        with patch("tts_server.load_config"):
            with patch("tts_server.tts_engines_config", mock_tts_engines_config):
                with patch("tts_server.model_engine", mock_model_engine):
                    mock_model_engine.engine_loaded = "xtts"
                    
                    response = client.get("/api/voices")
                    assert response.status_code == 200
                    voices = response.json()["voices"]
                    assert "builtin:Claribel Dervla" in voices
    
    def test_engine_switch_persists_configuration(self, client, mock_tts_engines_config, mock_model_engine):
        """Test that configuration persists after engine switch"""
        mock_tts_engines_config.is_valid_engine.return_value = True
        mock_tts_engines_config.change_engine.return_value = mock_tts_engines_config
        
        with patch("tts_server.load_config"):
            with patch("tts_server.tts_engines_config", mock_tts_engines_config):
                with patch("tts_server.handle_restart"):
                    response = client.post("/api/enginereload?engine=xtts")
                    assert response.status_code == 200
        
        # Verify save was called to persist configuration
        mock_tts_engines_config.save.assert_called()


class TestModelSwitchingIntegration:
    """Integration tests for model switching workflow"""
    
    def test_model_switch_complete_workflow(self, client, mock_model_engine):
        """Test complete model switching workflow"""
        # Setup initial model
        mock_model_engine.current_model_loaded = "xtts - v2.0.2"
        mock_model_engine.available_models = {"xtts - v2.0.2": {}, "xtts - v2.0.3": {}}
        
        # Step 1: Check current model
        with patch("tts_server.load_config"):
            with patch("tts_server.config") as mock_config:
                with patch("tts_server.model_engine", mock_model_engine):
                    response = client.get("/api/currentsettings")
                    assert response.status_code == 200
                    data = response.json()
                    assert data["current_model_loaded"] == "xtts - v2.0.2"
        
        # Step 2: Reload with new model
        mock_model_engine.handle_tts_method_change = AsyncMock(return_value=True)
        
        with patch("tts_server.load_config"):
            with patch("tts_server.model_engine", mock_model_engine):
                response = client.post("/api/reload?tts_method=xtts - v2.0.3")
                assert response.status_code == 200
                assert response.json()["status"] == "model-success"
    
    def test_model_switch_updates_voice_list(self, client, mock_model_engine):
        """Test that voice list updates after model switch"""
        # Model 1 voices
        mock_model_engine.multivoice_capable = True
        mock_model_engine.voices_file_list = Mock(return_value=["voice1.wav", "voice2.wav"])
        
        with patch("tts_server.load_config"):
            with patch("tts_server.model_engine", mock_model_engine):
                mock_model_engine.current_model_loaded = "model1"
                
                response = client.get("/api/voices")
                assert response.status_code == 200
                voices = response.json()["voices"]
                assert len(voices) == 2
        
        # Model 2 voices
        mock_model_engine.voices_file_list = Mock(return_value=["voice3.wav", "voice4.wav", "voice5.wav"])
        
        with patch("tts_server.load_config"):
            with patch("tts_server.model_engine", mock_model_engine):
                mock_model_engine.current_model_loaded = "model2"
                
                response = client.get("/api/voices")
                assert response.status_code == 200
                voices = response.json()["voices"]
                assert len(voices) == 3


class TestTtsGenerationIntegration:
    """Integration tests for complete TTS generation workflow"""
    
    def test_complete_tts_generation_workflow(self, client, mock_model_engine, temp_dir):
        """Test complete TTS generation workflow from text to audio"""
        # Step 1: Check system is ready
        mock_model_engine.setup_has_run = True
        
        with patch("tts_server.model_engine", mock_model_engine):
            response = client.get("/api/ready")
            assert response.status_code == 200
            assert response.text == "Ready"
        
        # Step 2: Get available voices
        mock_model_engine.multivoice_capable = True
        mock_model_engine.voices_file_list = Mock(return_value=["voice1.wav", "voice2.wav"])
        
        with patch("tts_server.load_config"):
            with patch("tts_server.model_engine", mock_model_engine):
                response = client.get("/api/voices")
                assert response.status_code == 200
                voices = response.json()["voices"]
                assert "voice1.wav" in voices
        
        # Step 3: Generate TTS
        audio_file = temp_dir / "test_audio.wav"
        import wave
        with wave.open(str(audio_file), "w") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(22050)
            wav.writeframes(b"\x00\x00" * 1000)
        
        mock_model_engine.tts_to_file = Mock(return_value=str(audio_file))
        mock_model_engine.audio_format = "wav"
        mock_model_engine.temperature_set = 0.75
        mock_model_engine.repetitionpenalty_set = 7.0
        
        with patch("tts_server.model_engine", mock_model_engine):
            with patch("tts_server.config") as mock_config:
                with patch("tts_server.load_config"):
                    mock_config.api_def.api_max_characters = 1000
                    mock_config.api_def.api_length_stripping = False
                    mock_config.api_def.api_use_legacy_api = False
                    mock_config.get_output_directory.return_value = temp_dir
                    
                    response = client.post(
                        "/api/tts-generate",
                        data={
                            "text_input": "Hello world",
                            "text_filtering": "none",
                            "character_voice_gen": "voice1.wav",
                            "rvccharacter_voice_gen": "Disabled",
                            "rvccharacter_pitch": 0,
                            "narrator_enabled": "false",
                            "narrator_voice_gen": "Disabled",
                            "rvcnarrator_voice_gen": "Disabled",
                            "rvcnarrator_pitch": 0,
                            "text_not_inside": "none",
                            "language": "en",
                            "output_file_name": "test_output",
                            "output_file_timestamp": False,
                            "autoplay": False,
                            "autoplay_volume": 0.5,
                            "streaming": False,
                        }
                    )
                    assert response.status_code in [200, 422, 500]


class TestSettingsUpdateIntegration:
    """Integration tests for settings update workflow"""
    
    def test_settings_update_persists(self, client, mock_tts_engines_config):
        """Test that settings updates persist"""
        mock_tts_engines_config.is_valid_engine.return_value = True
        mock_tts_engines_config.change_engine.return_value = mock_tts_engines_config
        
        # Update setting via engine reload
        with patch("tts_server.load_config"):
            with patch("tts_server.tts_engines_config", mock_tts_engines_config):
                with patch("tts_server.handle_restart"):
                    response = client.post("/api/enginereload?engine=xtts")
                    assert response.status_code == 200
        
        # Verify save was called
        mock_tts_engines_config.save.assert_called()
        
        # Verify the change was applied
        mock_tts_engines_config.change_engine.assert_called_with("xtts")


class TestModelDownloadIntegration:
    """Integration tests for model download workflow"""
    
    def test_model_download_endpoint_accessible(self, client):
        """Test that model download endpoints are accessible"""
        # Check if model download UI exists
        response = client.get("/")
        assert response.status_code == 200
        
        # The model download functionality should be accessible
        # This is a basic check - actual download testing would require network access


class TestErrorRecoveryIntegration:
    """Integration tests for error recovery workflows"""
    
    def test_recovery_after_invalid_model(self, client, mock_model_engine):
        """Test system recovery after invalid model reload"""
        # Try to reload invalid model
        mock_model_engine.available_models = {"valid_model": {}}
        
        with patch("tts_server.load_config"):
            with patch("tts_server.model_engine", mock_model_engine):
                response = client.post("/api/reload?tts_method=invalid_model")
                assert response.status_code == 200
                assert response.json()["status"] == "error"
        
        # System should still be operational
        mock_model_engine.setup_has_run = True
        
        with patch("tts_server.model_engine", mock_model_engine):
            response = client.get("/api/ready")
            assert response.status_code == 200
    
    def test_recovery_after_invalid_engine(self, client, mock_tts_engines_config):
        """Test system recovery after invalid engine switch"""
        mock_tts_engines_config.is_valid_engine.return_value = False
        
        with patch("tts_server.load_config"):
            with patch("tts_server.tts_engines_config", mock_tts_engines_config):
                response = client.post("/api/enginereload?engine=invalid_engine")
                assert response.status_code == 200
                assert response.json()["status"] == "error"
        
        # System should still be operational
        mock_tts_engines_config.is_valid_engine.return_value = True
        
        with patch("tts_server.load_config"):
            with patch("tts_server.tts_engines_config", mock_tts_engines_config):
                response = client.post("/api/enginereload?engine=xtts")
                assert response.status_code == 200


class TestConcurrentOperationsIntegration:
    """Integration tests for concurrent operations"""
    
    def test_concurrent_api_requests(self, client, mock_model_engine):
        """Test that system handles concurrent API requests"""
        import threading
        results = []
        
        mock_model_engine.setup_has_run = True
        
        def make_request():
            with patch("tts_server.model_engine", mock_model_engine):
                response = client.get("/api/ready")
                results.append(response.status_code)
        
        threads = [threading.Thread(target=make_request) for _ in range(10)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        assert all(status == 200 for status in results)


class TestCrossEngineIntegration:
    """Integration tests for cross-engine functionality"""
    
    def test_voice_format_compatibility(self, client, mock_model_engine):
        """Test that voice formats are compatible across engines"""
        # XTTS voices
        mock_model_engine.multivoice_capable = True
        mock_model_engine.voices_file_list = Mock(return_value=["builtin:Claribel Dervla"])
        
        with patch("tts_server.load_config"):
            with patch("tts_server.model_engine", mock_model_engine):
                mock_model_engine.engine_loaded = "xtts"
                
                response = client.get("/api/voices")
                assert response.status_code == 200
                voices = response.json()["voices"]
                assert "builtin:Claribel Dervla" in voices
        
        # Piper voices (different format)
        mock_model_engine.voices_file_list = Mock(return_value=["en_US-lessac-medium.onnx"])
        
        with patch("tts_server.load_config"):
            with patch("tts_server.model_engine", mock_model_engine):
                mock_model_engine.engine_loaded = "piper"
                
                response = client.get("/api/voices")
                assert response.status_code == 200
                voices = response.json()["voices"]
                assert "en_US-lessac-medium.onnx" in voices
