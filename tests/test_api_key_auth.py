# tests/test_api_key_auth.py
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from tts_server import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def _patched_config(api_key):
    """Return a config mock exposing the given api_key value."""
    mock_config = Mock()
    mock_config.api_def.api_key = api_key
    return mock_config


class TestApiKeyAuthDisabled:
    """With an empty api_key (the default), auth is off and behavior is unchanged."""

    def test_openai_speech_no_key_configured(self, client):
        with patch("tts_server.config", _patched_config("")):
            response = client.post(
                "/v1/audio/speech",
                json={"model": "tts-1", "input": "hi", "voice": "alloy"},
            )
            assert response.status_code != 401

    def test_native_tts_no_key_configured(self, client):
        with patch("tts_server.config", _patched_config("")):
            response = client.post("/api/tts-generate", data={})
            assert response.status_code != 401


class TestApiKeyAuthEnabled:
    """When api_key is set, protected generation endpoints require it."""

    API_KEY = "test-secret-key-123"

    def test_missing_key_openai_401_openai_shape(self, client):
        with patch("tts_server.config", _patched_config(self.API_KEY)):
            response = client.post(
                "/v1/audio/speech",
                json={"model": "tts-1", "input": "hi", "voice": "alloy"},
            )
            assert response.status_code == 401
            body = response.json()
            assert "error" in body
            assert body["error"]["code"] == "invalid_api_key"

    def test_missing_key_native_401(self, client):
        with patch("tts_server.config", _patched_config(self.API_KEY)):
            response = client.post("/api/tts-generate", data={})
            assert response.status_code == 401
            assert response.json()["status"] == "error"

    def test_wrong_key_401(self, client):
        with patch("tts_server.config", _patched_config(self.API_KEY)):
            response = client.post(
                "/v1/audio/speech",
                json={"model": "tts-1", "input": "hi", "voice": "alloy"},
                headers={"X-API-Key": "wrong-key"},
            )
            assert response.status_code == 401

    def test_correct_key_x_api_key_header(self, client):
        with patch("tts_server.config", _patched_config(self.API_KEY)):
            response = client.post(
                "/v1/audio/speech",
                json={"model": "tts-1", "input": "hi", "voice": "alloy"},
                headers={"X-API-Key": self.API_KEY},
            )
            assert response.status_code != 401

    def test_correct_key_bearer_header(self, client):
        with patch("tts_server.config", _patched_config(self.API_KEY)):
            response = client.post(
                "/v1/audio/speech",
                json={"model": "tts-1", "input": "hi", "voice": "alloy"},
                headers={"Authorization": "Bearer " + self.API_KEY},
            )
            assert response.status_code != 401

    def test_streaming_endpoint_protected(self, client):
        with patch("tts_server.config", _patched_config(self.API_KEY)):
            response = client.post("/api/tts-generate-streaming", data={})
            assert response.status_code == 401

    def test_unprotected_routes_stay_open(self, client):
        """Docs and non-generation endpoints remain reachable without a key."""
        with patch("tts_server.config", _patched_config(self.API_KEY)):
            assert client.get("/docs").status_code == 200
            assert client.get("/api/invalid_endpoint").status_code == 404
