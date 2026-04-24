"""
Unit tests for model download UI functions.
"""

import os
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

# Add the parent directory to the path to import the module
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from system.model_download_ui import check_model_status, get_model_info, get_available_models, get_model_details, filter_models


class TestCheckModelStatus:
    """Tests for check_model_status function."""
    
    def test_no_models_directory(self, tmp_path):
        """Test when models directory doesn't exist."""
        # Create a temporary directory structure
        this_dir = tmp_path
        
        with patch('system.model_download_ui.this_dir', this_dir):
            exists, message = check_model_status("xtts")
            assert not exists
            assert "No models found" in message
    
    def test_empty_models_directory(self, tmp_path):
        """Test when models directory exists but has no model files."""
        models_dir = tmp_path / "models" / "xtts"
        models_dir.mkdir(parents=True)
        
        with patch('system.model_download_ui.this_dir', tmp_path):
            exists, message = check_model_status("xtts")
            assert not exists
            assert "no model files found" in message.lower()
    
    def test_models_with_files(self, tmp_path):
        """Test when models directory has model files."""
        models_dir = tmp_path / "models" / "xtts"
        models_dir.mkdir(parents=True)
        
        # Create a fake model file
        (models_dir / "model.pth").write_bytes(b"fake model data")
        
        with patch('system.model_download_ui.this_dir', tmp_path):
            exists, message = check_model_status("xtts")
            assert exists
            assert "model downloaded" in message.lower() or "model files found" in message.lower()


class TestGetModelInfo:
    """Tests for get_model_info function."""
    
    def test_no_available_models_json(self, tmp_path):
        """Test when available_models.json doesn't exist."""
        with patch('system.model_download_ui.this_dir', tmp_path):
            info = get_model_info("xtts")
            assert "available_models.json" in info
            assert "not present" in info
            assert "Alternative download methods" in info
    
    def test_with_available_models_json(self, tmp_path):
        """Test when available_models.json exists."""
        # Create the directory structure
        engine_dir = tmp_path / "system" / "tts_engines" / "xtts"
        engine_dir.mkdir(parents=True)
        
        # Create a fake available_models.json
        models_data = {
            "first_start_model": "xttsv2_2.0.3",
            "models": [
                {"model_name": "xttsv2_2.0.3", "description": "Default XTTS model"},
                {"model_name": "xttsv2_2.0.2", "description": "Previous version"}
            ]
        }
        
        with open(engine_dir / "available_models.json", "w") as f:
            json.dump(models_data, f)
        
        with patch('system.model_download_ui.this_dir', tmp_path):
            info = get_model_info("xtts")
            assert "XTTS Models" in info
            assert "xttsv2_2.0.3" in info
            assert "xttsv2_2.0.2" in info
    
    def test_corrupted_available_models_json(self, tmp_path):
        """Test when available_models.json is corrupted."""
        engine_dir = tmp_path / "system" / "tts_engines" / "xtts"
        engine_dir.mkdir(parents=True)
        
        # Create a corrupted JSON file
        with open(engine_dir / "available_models.json", "w") as f:
            f.write("invalid json {")
        
        with patch('system.model_download_ui.this_dir', tmp_path):
            info = get_model_info("xtts")
            assert "Error reading model info" in info


class TestDownloadModelAsync:
    """Tests for download_model_async function."""
    
    @patch('system.config.firstrun.download_tts_model')
    @patch('system.config.firstrun.update_tts_engines')
    def test_successful_download(self, mock_update, mock_download):
        """Test successful model download."""
        mock_download.return_value = True
        
        from system.model_download_ui import download_model_async
        
        result = download_model_async("xtts")
        
        assert "Successfully downloaded" in result
        mock_download.assert_called_once()
        assert mock_download.call_args[0][0] == "xtts"  # First arg is engine
        mock_update.assert_called_once_with("xtts")
    
    @patch('system.config.firstrun.download_tts_model')
    def test_failed_download(self, mock_download):
        """Test failed model download."""
        mock_download.return_value = False
        
        from system.model_download_ui import download_model_async
        
        result = download_model_async("xtts")
        
        assert "Failed to download" in result
        mock_download.assert_called_once()
        assert mock_download.call_args[0][0] == "xtts"  # First arg is engine
    
    @patch('system.config.firstrun.download_tts_model')
    def test_download_exception(self, mock_download):
        """Test download with exception."""
        mock_download.side_effect = Exception("Test error")
        
        from system.model_download_ui import download_model_async
        
        result = download_model_async("xtts")
        
        assert "Error during download" in result
        assert "Test error" in result
    
    @patch('system.config.firstrun.download_tts_model')
    @patch('system.config.firstrun.update_tts_engines')
    def test_download_with_progress_callback(self, mock_update, mock_download):
        """Test download with progress callback."""
        mock_download.return_value = True
        progress_updates = []
        
        def mock_progress(progress, desc):
            progress_updates.append((progress, desc))
        
        from system.model_download_ui import download_model_async
        
        result = download_model_async("xtts", progress=mock_progress)
        
        assert "Successfully downloaded" in result
        # Verify progress callback was called
        assert len(progress_updates) > 0
        # Verify download_tts_model was called with progress_callback
        mock_download.assert_called_once()
        # Check that progress_callback was passed
        call_args = mock_download.call_args
        assert 'progress_callback' in call_args.kwargs


class TestGetModelInfoPiperGrouping:
    """Tests for Piper model grouping and formatting."""
    
    def test_piper_models_grouped_by_language(self, tmp_path):
        """Test that Piper models are grouped by language."""
        engine_dir = tmp_path / "system" / "tts_engines" / "piper"
        engine_dir.mkdir(parents=True)
        
        models_data = {
            "first_start_model": "en_US-ljspeech-high",
            "models": [
                {"model_name": "en_US-ljspeech-high", "files_to_download": []},
                {"model_name": "en_US-amy-medium", "files_to_download": []},
                {"model_name": "ar_JO-kareem-low", "files_to_download": []},
                {"model_name": "es_ES-davefx-medium", "files_to_download": []}
            ]
        }
        
        with open(engine_dir / "available_models.json", "w") as f:
            json.dump(models_data, f)
        
        with patch('system.model_download_ui.this_dir', tmp_path):
            info = get_model_info("piper")
            
            # Check that languages are grouped
            assert "**en_US:**" in info
            assert "**ar_JO:**" in info
            assert "**es_ES:**" in info
    
    def test_piper_quality_indicators(self, tmp_path):
        """Test that Piper models show quality indicators."""
        engine_dir = tmp_path / "system" / "tts_engines" / "piper"
        engine_dir.mkdir(parents=True)
        
        models_data = {
            "first_start_model": "en_US-ljspeech-high",
            "models": [
                {"model_name": "en_US-ljspeech-high", "files_to_download": []},
                {"model_name": "en_US-amy-medium", "files_to_download": []},
                {"model_name": "en_US-ryan-low", "files_to_download": []},
                {"model_name": "ca_ES-upc_ona-x_low", "files_to_download": []}
            ]
        }
        
        with open(engine_dir / "available_models.json", "w") as f:
            json.dump(models_data, f)
        
        with patch('system.model_download_ui.this_dir', tmp_path):
            info = get_model_info("piper")
            
            # Check quality emojis are present
            assert "🔴" in info  # high
            assert "🟡" in info  # medium
            assert "🟢" in info  # low
            assert "🔹" in info  # x_low
    
    def test_piper_quality_legend(self, tmp_path):
        """Test that Piper model info includes quality legend."""
        engine_dir = tmp_path / "system" / "tts_engines" / "piper"
        engine_dir.mkdir(parents=True)
        
        models_data = {
            "first_start_model": "en_US-ljspeech-high",
            "models": [{"model_name": "en_US-ljspeech-high", "files_to_download": []}]
        }
        
        with open(engine_dir / "available_models.json", "w") as f:
            json.dump(models_data, f)
        
        with patch('system.model_download_ui.this_dir', tmp_path):
            info = get_model_info("piper")
            
            # Check quality legend is present
            assert "Quality legend" in info
            assert "🔴=high" in info
            assert "🟡=medium" in info
            assert "🟢=low" in info
            assert "🔹=x_low" in info


class TestGetAvailableModels:
    """Tests for get_available_models function."""
    
    def test_no_available_models_json(self, tmp_path):
        """Test when available_models.json doesn't exist."""
        with patch('system.model_download_ui.this_dir', tmp_path):
            models = get_available_models("xtts")
            assert models == []
    
    def test_with_available_models_json(self, tmp_path):
        """Test when available_models.json exists."""
        engine_dir = tmp_path / "system" / "tts_engines" / "xtts"
        engine_dir.mkdir(parents=True)
        
        models_data = {
            "first_start_model": "xttsv2_2.0.3",
            "models": [
                {"model_name": "xttsv2_2.0.3", "files_to_download": []},
                {"model_name": "xttsv2_2.0.2", "files_to_download": []}
            ]
        }
        
        with open(engine_dir / "available_models.json", "w") as f:
            json.dump(models_data, f)
        
        with patch('system.model_download_ui.this_dir', tmp_path):
            models = get_available_models("xtts")
            assert len(models) == 2
            assert "xttsv2_2.0.3" in models
            assert "xttsv2_2.0.2" in models
    
    def test_corrupted_available_models_json(self, tmp_path):
        """Test when available_models.json is corrupted."""
        engine_dir = tmp_path / "system" / "tts_engines" / "xtts"
        engine_dir.mkdir(parents=True)
        
        with open(engine_dir / "available_models.json", "w") as f:
            f.write("invalid json {")
        
        with patch('system.model_download_ui.this_dir', tmp_path):
            models = get_available_models("xtts")
            assert models == []
    
    def test_piper_models_list(self, tmp_path):
        """Test getting Piper models list."""
        engine_dir = tmp_path / "system" / "tts_engines" / "piper"
        engine_dir.mkdir(parents=True)
        
        models_data = {
            "first_start_model": "en_US-ljspeech-high",
            "models": [
                {"model_name": "en_US-ljspeech-high", "files_to_download": []},
                {"model_name": "en_US-amy-medium", "files_to_download": []},
                {"model_name": "ar_JO-kareem-low", "files_to_download": []}
            ]
        }
        
        with open(engine_dir / "available_models.json", "w") as f:
            json.dump(models_data, f)
        
        with patch('system.model_download_ui.this_dir', tmp_path):
            models = get_available_models("piper")
            assert len(models) == 3
            assert "en_US-ljspeech-high" in models
            assert "en_US-amy-medium" in models
            assert "ar_JO-kareem-low" in models


class TestGetModelDetails:
    """Tests for get_model_details function."""
    
    def test_no_available_models_json(self, tmp_path):
        """Test when available_models.json doesn't exist."""
        with patch('system.model_download_ui.this_dir', tmp_path):
            details = get_model_details("xtts")
            assert details == []
    
    def test_piper_model_details(self, tmp_path):
        """Test getting Piper model details."""
        engine_dir = tmp_path / "system" / "tts_engines" / "piper"
        engine_dir.mkdir(parents=True)
        
        models_data = {
            "first_start_model": "en_US-ljspeech-high",
            "models": [
                {"model_name": "en_US-ljspeech-high", "files_to_download": []},
                {"model_name": "en_US-amy-medium", "files_to_download": []},
                {"model_name": "ar_JO-kareem-low", "files_to_download": []}
            ]
        }
        
        with open(engine_dir / "available_models.json", "w") as f:
            json.dump(models_data, f)
        
        with patch('system.model_download_ui.this_dir', tmp_path):
            details = get_model_details("piper")
            assert len(details) == 3
            assert details[0]['name'] == "en_US-ljspeech-high"
            assert details[0]['language'] == "en_US"
            assert details[0]['quality'] == "high"
            assert details[1]['quality'] == "medium"
            assert details[2]['quality'] == "low"


class TestFilterModels:
    """Tests for filter_models function."""
    
    def test_filter_by_language(self):
        """Test filtering models by language."""
        models = [
            {'name': 'en_US-ljspeech-high', 'language': 'en_US', 'quality': 'high'},
            {'name': 'en_US-amy-medium', 'language': 'en_US', 'quality': 'medium'},
            {'name': 'ar_JO-kareem-low', 'language': 'ar_JO', 'quality': 'low'}
        ]
        
        filtered = filter_models(models, language_filter="en_US")
        assert len(filtered) == 2
        assert all(m['language'] == 'en_US' for m in filtered)
    
    def test_filter_by_quality(self):
        """Test filtering models by quality."""
        models = [
            {'name': 'en_US-ljspeech-high', 'language': 'en_US', 'quality': 'high'},
            {'name': 'en_US-amy-medium', 'language': 'en_US', 'quality': 'medium'},
            {'name': 'ar_JO-kareem-low', 'language': 'ar_JO', 'quality': 'low'}
        ]
        
        filtered = filter_models(models, quality_filter="high")
        assert len(filtered) == 1
        assert filtered[0]['quality'] == 'high'
    
    def test_filter_by_both(self):
        """Test filtering models by both language and quality."""
        models = [
            {'name': 'en_US-ljspeech-high', 'language': 'en_US', 'quality': 'high'},
            {'name': 'en_US-amy-medium', 'language': 'en_US', 'quality': 'medium'},
            {'name': 'ar_JO-kareem-low', 'language': 'ar_JO', 'quality': 'low'}
        ]
        
        filtered = filter_models(models, language_filter="en_US", quality_filter="high")
        assert len(filtered) == 1
        assert filtered[0]['name'] == 'en_US-ljspeech-high'
    
    def test_no_filters(self):
        """Test that no filters returns all models."""
        models = [
            {'name': 'en_US-ljspeech-high', 'language': 'en_US', 'quality': 'high'},
            {'name': 'en_US-amy-medium', 'language': 'en_US', 'quality': 'medium'}
        ]
        
        filtered = filter_models(models)
        assert len(filtered) == 2


class TestSelectAllAndClear:
    """Tests for Select All and Clear Selection functionality."""
    
    def test_on_select_all_with_filters(self):
        """Test that Select All selects all filtered models."""
        models = [
            {'name': 'en_US-ljspeech-high', 'language': 'en_US', 'quality': 'high'},
            {'name': 'en_US-amy-medium', 'language': 'en_US', 'quality': 'medium'},
            {'name': 'ar_JO-kareem-low', 'language': 'ar_JO', 'quality': 'low'}
        ]
        
        filtered = filter_models(models, language_filter="en_US")
        selected = [m['name'] for m in filtered]
        
        assert len(selected) == 2
        assert 'en_US-ljspeech-high' in selected
        assert 'en_US-amy-medium' in selected
    
    def test_on_select_all_no_filters(self):
        """Test that Select All with no filters selects all models."""
        models = [
            {'name': 'en_US-ljspeech-high', 'language': 'en_US', 'quality': 'high'},
            {'name': 'en_US-amy-medium', 'language': 'en_US', 'quality': 'medium'}
        ]
        
        filtered = filter_models(models)
        selected = [m['name'] for m in filtered]
        
        assert len(selected) == 2
        assert 'en_US-ljspeech-high' in selected
        assert 'en_US-amy-medium' in selected


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
