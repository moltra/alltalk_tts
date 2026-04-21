"""
Tests for subprocess security fixes in diagnostics.py.

This test verifies that subprocess calls don't use shell=True
and that command validation is in place to prevent injection.
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Import the functions from diagnostics
from diagnostics import ALLOWED_PIP_COMMANDS, execute_pip_command


class TestSubprocessSecurity:
    """Test subprocess security fixes"""

    def test_command_whitelist_exists(self):
        """Test that ALLOWED_PIP_COMMANDS whitelist exists"""
        assert isinstance(ALLOWED_PIP_COMMANDS, list)
        assert len(ALLOWED_PIP_COMMANDS) > 0
        assert "install" in ALLOWED_PIP_COMMANDS
        assert "uninstall" in ALLOWED_PIP_COMMANDS

    def test_execute_pip_command_allowed(self):
        """Test that allowed commands execute successfully"""
        with patch("subprocess.run") as mock_subprocess:
            mock_subprocess.return_value = Mock(returncode=0, stdout="", stderr="")

            execute_pip_command("install numpy")
            assert mock_subprocess.called
            # Verify the command was called with list arguments, not shell=True
            call_args = mock_subprocess.call_args
            assert "shell" not in call_args.kwargs or call_args.kwargs["shell"] is False

    def test_execute_pip_command_disallowed(self):
        """Test that disallowed commands raise ValueError"""
        with pytest.raises(ValueError, match="Command not allowed"):
            execute_pip_command("rm -rf /")

    def test_execute_pip_command_empty(self):
        """Test that empty commands raise ValueError"""
        with pytest.raises(ValueError, match="Empty command"):
            execute_pip_command("")

    def test_execute_pip_command_injection_attempt(self):
        """Test that command injection attempts are blocked"""
        with pytest.raises(ValueError, match="dangerous characters"):
            execute_pip_command("install numpy; rm -rf /")

    @patch("subprocess.run")
    def test_subprocess_no_shell_true(self, mock_subprocess):
        """Test that subprocess.run is called without shell=True"""
        mock_subprocess.return_value = Mock(returncode=0, stdout="", stderr="")

        execute_pip_command("list")

        call_args = mock_subprocess.call_args
        if "shell" in call_args.kwargs:
            assert call_args.kwargs["shell"] is False

    def test_no_os_system_in_clear_screen(self):
        """Test that clear_screen doesn't use os.system"""
        # Read the diagnostics.py file
        diagnostics_path = Path(__file__).parent.parent / "diagnostics.py"
        with diagnostics_path.open() as f:
            content = f.read()

        # Check that os.system("cls") is NOT present
        assert 'os.system("cls")' not in content, "Found os.system('cls') - should use subprocess instead"

        # Check that os.system("clear") is NOT present
        assert 'os.system("clear")' not in content, "Found os.system('clear') - should use subprocess instead"

        # Check that subprocess.run is used instead
        assert (
            'subprocess.run(["cmd", "/c", "cls"]' in content or 'subprocess.run(["clear"]' in content
        ), "subprocess.run for screen clearing not found"

    def test_subprocess_uses_list_not_string(self):
        """Test that subprocess.run uses list arguments instead of shell=True"""
        with patch("subprocess.run") as mock_subprocess:
            mock_subprocess.return_value = Mock(returncode=0, stdout="", stderr="")

            execute_pip_command("install numpy")

            # Verify the first argument is a list
            call_args = mock_subprocess.call_args[0][0]
            assert isinstance(call_args, list)
            assert call_args[0] == sys.executable
            assert call_args[1] == "-m"
            assert call_args[2] == "pip"
