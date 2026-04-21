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
            assert response.status_code == 500
            assert "does not support multiple voices" in response.json()["message"]


class TestAudioEndpoint:
    def test_get_audio_success(self, client, test_audio_file):
        """Test getting audio file"""
        with patch("tts_server.config") as mock_config:
            mock_config.get_output_directory.return_value = test_audio_file.parent

            response = client.get(f"/audio/{test_audio_file.name}")
            assert response.status_code == 200
            assert response.headers["content-type"] == "audio/wav"

    def test_get_audio_not_found(self, client):
        """Test getting non-existent audio file"""
        with patch("tts_server.config") as mock_config:
            mock_config.get_output_directory.return_value = Path("/fake/path")

            response = client.get("/audio/nonexistent.wav")
            assert response.status_code == 404


class TestCorsSettings:
    def test_cors_environment_variable(self, monkeypatch):
        """Test CORS settings can be overridden via environment variable"""
        from config import AlltalkConfigCorsSettings

        monkeypatch.setenv("ALLTALK_ALLOWED_ORIGINS", "http://example.com,http://test.com")
        cors_settings = AlltalkConfigCorsSettings()

        assert "http://example.com" in cors_settings.allowed_origins
        assert "http://test.com" in cors_settings.allowed_origins
        assert len(cors_settings.allowed_origins) == 2

    def test_cors_default_origins(self, monkeypatch):
        """Test CORS settings use default when no environment variable"""
        from config import AlltalkConfigCorsSettings

        monkeypatch.delenv("ALLTALK_ALLOWED_ORIGINS", raising=False)
        cors_settings = AlltalkConfigCorsSettings()

        assert "http://localhost:7852" in cors_settings.allowed_origins
        assert "http://localhost:3000" in cors_settings.allowed_origins
