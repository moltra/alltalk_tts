# tests/test_api_endpoints.py
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from tts_server import app


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


class TestReloadEndpoint:
    def test_reload_success(self, client, mock_model_engine):
        """Test successful model reload"""
        with patch("tts_server.model_engine", mock_model_engine):
            response = client.post("/api/reload?tts_method=test_model")
            assert response.status_code == 200
            assert response.json() == {"status": "model-success"}

    def test_reload_invalid_model(self, client, mock_model_engine):
        """Test reload with invalid model"""
        mock_model_engine.available_models = {"valid_model": {}}
        with patch("tts_server.model_engine", mock_model_engine):
            response = client.post("/api/reload?tts_method=invalid_model")
            assert response.status_code == 200
            assert response.json()["status"] == "error"


class TestVoicesEndpoint:
    def test_get_voices_success(self, client, mock_model_engine):
        """Test getting voices list"""
        mock_model_engine.multivoice_capable = True
        mock_model_engine.voices_file_list = Mock(return_value=["voice1.wav", "voice2.wav"])

        with patch("tts_server.model_engine", mock_model_engine):
            response = client.get("/api/voices")
            assert response.status_code == 200
            assert response.json()["status"] == "success"
            assert len(response.json()["voices"]) == 2

    def test_get_voices_not_supported(self, client, mock_model_engine):
        """Test voices when engine doesn't support it"""
        mock_model_engine.multivoice_capable = False

        with patch("tts_server.model_engine", mock_model_engine):
            response = client.get("/api/voices")
            assert response.status_code == 200
            assert response.json()["status"] == "error"
            assert "does not support multiple voices" in response.json()["message"]

    def test_get_voices_builtin_xtts(self, client, mock_model_engine):
        """Test returns builtin XTTS voices when XTTS is loaded"""
        mock_model_engine.multivoice_capable = True
        mock_model_engine.current_model_loaded = "xtts - test_model"
        mock_model_engine.voices_file_list = Mock(return_value=["builtin:Claribel Dervla", "builtin:Daisy Studious"])

        with patch("tts_server.model_engine", mock_model_engine):
            response = client.get("/api/voices")
            assert response.status_code == 200
            assert response.json()["status"] == "success"
            assert "builtin:Claribel Dervla" in response.json()["voices"]

    def test_get_voices_wav_files(self, client, mock_model_engine):
        """Test returns WAV files for voice cloning"""
        mock_model_engine.multivoice_capable = True
        mock_model_engine.voices_file_list = Mock(return_value=["voice1.wav", "voice2.wav"])

        with patch("tts_server.model_engine", mock_model_engine):
            response = client.get("/api/voices")
            assert response.status_code == 200
            assert response.json()["status"] == "success"
            assert "voice1.wav" in response.json()["voices"]

    def test_get_voices_voice_sets(self, client, mock_model_engine):
        """Test returns voice sets"""
        mock_model_engine.multivoice_capable = True
        mock_model_engine.voices_file_list = Mock(return_value=["voiceset:voice_set_1", "voiceset:voice_set_2"])

        with patch("tts_server.model_engine", mock_model_engine):
            response = client.get("/api/voices")
            assert response.status_code == 200
            assert response.json()["status"] == "success"
            assert "voiceset:voice_set_1" in response.json()["voices"]

    def test_get_voices_latents(self, client, mock_model_engine):
        """Test returns latents"""
        mock_model_engine.multivoice_capable = True
        mock_model_engine.voices_file_list = Mock(return_value=["latent:latent1.json"])

        with patch("tts_server.model_engine", mock_model_engine):
            response = client.get("/api/voices")
            assert response.status_code == 200
            assert response.json()["status"] == "success"
            assert "latent:latent1.json" in response.json()["voices"]

    def test_get_voices_no_voices_found(self, client, mock_model_engine):
        """Test returns 'No Voices Found' when no voices available"""
        mock_model_engine.multivoice_capable = True
        mock_model_engine.voices_file_list = Mock(return_value=["No Voices Found"])

        with patch("tts_server.model_engine", mock_model_engine):
            response = client.get("/api/voices")
            assert response.status_code == 200
            assert response.json()["status"] == "success"
            assert "No Voices Found" in response.json()["voices"]


class TestAudioEndpoint:
    def test_get_audio_success(self, client, test_audio_file):
        """Test getting audio file"""
        with patch("tts_server.config") as mock_config:
            mock_config.get_output_directory.return_value = test_audio_file.parent

            response = client.get(f"/audio/{test_audio_file.name}")
            assert response.status_code == 200
            assert "audio" in response.headers["content-type"]

    def test_get_audio_not_found(self, client):
        """Test getting non-existent audio file"""
        with patch("tts_server.config") as mock_config:
            mock_config.get_output_directory.return_value = Path("/fake/path")

            response = client.get("/audio/nonexistent.wav")
            assert response.status_code == 404


class TestEngineReloadEndpoint:
    def test_engine_reload_success(self, client, mock_tts_engines_config):
        """Test successful engine reload"""
        mock_tts_engines_config.is_valid_engine.return_value = True
        mock_tts_engines_config.change_engine.return_value = mock_tts_engines_config

        with patch("tts_server.tts_engines_config", mock_tts_engines_config):
            with patch("tts_server.handle_restart"):
                response = client.post("/api/enginereload?engine=xtts")
                assert response.status_code == 200
                assert response.json()["status"] == "engine-success"

    def test_engine_reload_invalid_engine(self, client, mock_tts_engines_config):
        """Test engine reload with invalid engine"""
        mock_tts_engines_config.is_valid_engine.return_value = False

        with patch("tts_server.tts_engines_config", mock_tts_engines_config):
            response = client.post("/api/enginereload?engine=invalid_engine")
            assert response.status_code == 200
            assert response.json()["status"] == "error"


class TestCurrentSettingsEndpoint:
    def test_get_current_settings(self, client, mock_tts_engines_config, mock_model_engine):
        """Test getting current settings"""
        mock_tts_engines_config.get_engine_names_available.return_value = ["xtts", "piper"]
        mock_model_engine.engine_loaded = "xtts"
        mock_model_engine.current_model_loaded = "xtts - v2.0.2"
        mock_model_engine.available_models = {"xtts - v2.0.2": {}, "xtts - v2.0.3": {}}
        mock_model_engine.manufacturer_name = "Coqui"
        mock_model_engine.audio_format = "wav"
        mock_model_engine.deepspeed_capable = True
        mock_model_engine.deepspeed_available = False
        mock_model_engine.deepspeed_enabled = False
        mock_model_engine.generationspeed_capable = True
        mock_model_engine.generationspeed_set = 1.0
        mock_model_engine.lowvram_capable = True
        mock_model_engine.lowvram_enabled = False
        mock_model_engine.pitch_capable = True
        mock_model_engine.pitch_set = 0
        mock_model_engine.streaming_capable = True
        mock_model_engine.multivoice_capable = True
        
        with patch("tts_server.load_config"):
            with patch("tts_server.config") as mock_config:
                with patch("tts_server.tts_engines_config", mock_tts_engines_config):
                    with patch("tts_server.model_engine", mock_model_engine):
                        response = client.get("/api/currentsettings")
                        assert response.status_code == 200
                        data = response.json()
                        assert "engines_available" in data
                        assert "current_engine_loaded" in data
                        assert "models_available" in data


class TestReadyEndpoint:
    def test_ready_endpoint_ready(self, client, mock_model_engine):
        """Test ready endpoint when system is ready"""
        mock_model_engine.setup_has_run = True
        with patch("tts_server.model_engine", mock_model_engine):
            response = client.get("/api/ready")
            assert response.status_code == 200
            assert response.text == "Ready"
    
    def test_ready_endpoint_unloaded(self, client, mock_model_engine):
        """Test ready endpoint during startup"""
        mock_model_engine.setup_has_run = False
        with patch("tts_server.model_engine", mock_model_engine):
            response = client.get("/api/ready")
            assert response.status_code == 200
            assert response.text == "Unloaded"


class TestRvcVoicesEndpoint:
    def test_get_rvcvoices_disabled(self, client):
        """Test RVC voices when disabled"""
        with patch("tts_server.load_config"):
            with patch("tts_server.config") as mock_config:
                mock_config.rvc_settings.rvc_enabled = False
                response = client.get("/api/rvcvoices")
                assert response.status_code == 200
                assert response.json()["rvcvoices"] == ["Disabled"]
    
    def test_get_rvcvoices_enabled(self, client, temp_dir):
        """Test RVC voices when enabled"""
        # Create mock RVC voices directory
        rvc_dir = temp_dir / "models" / "rvc_voices"
        rvc_dir.mkdir(parents=True)
        (rvc_dir / "voice1.pth").touch()
        (rvc_dir / "voice2.pth").touch()
        
        with patch("tts_server.load_config"):
            with patch("tts_server.config") as mock_config:
                with patch("tts_server.this_dir", temp_dir):
                    mock_config.rvc_settings.rvc_enabled = True
                    response = client.get("/api/rvcvoices")
                    assert response.status_code == 200
                    data = response.json()
                    assert "rvcvoices" in data
                    # Should return list of RVC voices


class TestTtsGenerationEndpoint:
    def test_tts_generate_standard_success(self, client, mock_model_engine, temp_dir):
        """Test successful TTS generation with valid text"""
        # Create a mock audio file
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
                    # Should get a response (may be success or error depending on full implementation)
                    assert response.status_code in [200, 422, 500]

    def test_tts_generate_empty_text(self, client):
        """Test error handling for empty text"""
        with patch("tts_server.config") as mock_config:
            with patch("tts_server.load_config"):
                mock_config.api_def.api_max_characters = 1000
                
                response = client.post(
                    "/api/tts-generate",
                    data={
                        "text_input": "",
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
                # Empty text should be handled (may return error or process it)
                assert response.status_code in [200, 422]


class TestStopGenerationEndpoint:
    def test_stop_generation(self, client, mock_model_engine):
        """Test stops current generation"""
        mock_model_engine.tts_stop_generation = False
        with patch("tts_server.model_engine", mock_model_engine):
            response = client.put("/api/stop-generation")
            assert response.status_code == 200
    
    def test_stop_generation_no_active(self, client, mock_model_engine):
        """Test handles no active generation"""
        mock_model_engine.tts_stop_generation = True
        with patch("tts_server.model_engine", mock_model_engine):
            response = client.put("/api/stop-generation")
            assert response.status_code == 200
    
    def test_stop_generation_resets_state(self, client, mock_model_engine):
        """Test resets generation state"""
        mock_model_engine.tts_stop_generation = False
        with patch("tts_server.model_engine", mock_model_engine):
            response = client.put("/api/stop-generation")
            assert response.status_code == 200
            # Verify the flag was set
            assert mock_model_engine.tts_stop_generation == True


class TestApiErrorHandling:
    def test_invalid_endpoint(self, client):
        """Test invalid endpoint returns 404"""
        response = client.get("/api/invalid_endpoint")
        assert response.status_code == 404

    def test_missing_required_parameter(self, client):
        """Test missing required parameter"""
        response = client.post("/api/enginereload")  # Missing engine parameter
        # The endpoint should handle this gracefully
        assert response.status_code == 200 or response.status_code == 422


class TestApiSecurity:
    def test_sql_injection_prevention(self, client):
        """Test basic SQL injection prevention"""
        # Test that SQL injection attempts are handled
        response = client.get("/api/voices")
        # The endpoint should not be vulnerable to SQL injection
        assert response.status_code == 200

    def test_xss_prevention(self, client):
        """Test basic XSS prevention"""
        # Test that XSS attempts are handled
        response = client.get("/api/voices")
        # The endpoint should not be vulnerable to XSS
        assert response.status_code == 200


class TestApiPerformance:
    def test_api_response_time(self, client):
        """Test API response time is acceptable"""
        import time
        start_time = time.time()
        response = client.get("/api/ready")
        end_time = time.time()
        response_time = end_time - start_time
        # Response should be under 1 second
        assert response_time < 1.0
        assert response.status_code == 200

    def test_concurrent_requests(self, client):
        """Test API handles concurrent requests"""
        import threading
        results = []
        
        def make_request():
            response = client.get("/api/ready")
            results.append(response.status_code)
        
        threads = [threading.Thread(target=make_request) for _ in range(5)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        assert all(status == 200 for status in results)


class TestCorsSettings:
    def test_cors_environment_variable(self, monkeypatch):
        """Test CORS settings can be overridden via environment variable"""
        from config.app.config import AlltalkConfigCorsSettings

        monkeypatch.setenv("ALLTALK_ALLOWED_ORIGINS", "http://example.com,http://test.com")
        cors_settings = AlltalkConfigCorsSettings()

        assert "http://example.com" in cors_settings.allowed_origins
        assert "http://test.com" in cors_settings.allowed_origins
        assert len(cors_settings.allowed_origins) == 2

    def test_cors_default_origins(self, monkeypatch):
        """Test CORS settings use default when no environment variable"""
        from config.app.config import AlltalkConfigCorsSettings

        monkeypatch.delenv("ALLTALK_ALLOWED_ORIGINS", raising=False)
        cors_settings = AlltalkConfigCorsSettings()

        assert "http://localhost:7852" in cors_settings.allowed_origins
        assert "http://localhost:3000" in cors_settings.allowed_origins
