"""
Tests for CORS configuration security fix.

This test verifies that CORS is configured with specific origins
instead of allowing all origins, which is a security vulnerability.
"""
import pytest
from pathlib import Path
import tempfile
import shutil

from config import AlltalkConfig, AlltalkConfigCorsSettings


class TestCorsConfiguration:
    """Test CORS configuration for security compliance"""
    
    def test_cors_settings_default_origins(self):
        """Test that CORS settings have specific default origins, not wildcard"""
        cors_settings = AlltalkConfigCorsSettings()
        
        # Should have specific origins, not wildcard
        assert cors_settings.allowed_origins is not None
        assert isinstance(cors_settings.allowed_origins, list)
        assert len(cors_settings.allowed_origins) > 0
        
        # Should not contain wildcard
        assert "*" not in cors_settings.allowed_origins
        
        # Should contain localhost origins for development
        assert any("localhost" in origin for origin in cors_settings.allowed_origins)
    
    def test_cors_settings_credentials_enabled(self):
        """Test that credentials can be enabled with specific origins"""
        cors_settings = AlltalkConfigCorsSettings()
        
        # Credentials should be True by default for development
        assert cors_settings.allow_credentials is True
    
    def test_config_includes_cors_settings(self, temp_dir):
        """Test that AlltalkConfig includes CORS settings"""
        config_path = temp_dir / "test_config.json"
        
        # Create minimal config file first
        import json
        with open(config_path, 'w') as f:
            json.dump({}, f)
        
        config = AlltalkConfig(config_path=config_path)
        
        # Should have cors_settings attribute
        assert hasattr(config, 'cors_settings')
        assert isinstance(config.cors_settings, AlltalkConfigCorsSettings)
    
    def test_cors_settings_persistence(self, temp_dir):
        """Test that CORS settings persist through save/load"""
        config_path = temp_dir / "test_config.json"
        
        # Create minimal config file first
        import json
        with open(config_path, 'w') as f:
            json.dump({}, f)
        
        config = AlltalkConfig(config_path=config_path)
        
        # Modify CORS settings
        custom_origins = ["http://custom-origin:8080", "https://example.com"]
        config.cors_settings.allowed_origins = custom_origins
        config.save()
        
        # Load new instance
        config2 = AlltalkConfig(config_path=config_path)
        
        # Should persist custom origins
        assert config2.cors_settings.allowed_origins == custom_origins
    
    def test_cors_settings_not_wildcard_in_config(self, temp_dir):
        """Test that saved config doesn't contain wildcard origins"""
        config_path = temp_dir / "test_config.json"
        
        # Create minimal config file first
        import json
        with open(config_path, 'w') as f:
            json.dump({}, f)
        
        config = AlltalkConfig(config_path=config_path)
        config.save()
        
        # Read the JSON file
        with open(config_path, 'r') as f:
            config_data = json.load(f)
        
        # Verify allowed_origins doesn't contain wildcard
        if 'cors_settings' in config_data and 'allowed_origins' in config_data['cors_settings']:
            assert "*" not in config_data['cors_settings']['allowed_origins']


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests"""
    temp = tempfile.mkdtemp()
    yield Path(temp)
    shutil.rmtree(temp)
