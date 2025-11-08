"""Tests for Windows-specific Bash tool functionality"""
import platform
import pytest

from tools.bash import normalize_windows_path, _IS_WINDOWS, _USING_GIT_BASH


class TestWindowsPathConversion:
    """Test Windows path conversion to Git Bash format"""

    def test_simple_path_conversion(self):
        """Test basic Windows path conversion"""
        if not _IS_WINDOWS or not _USING_GIT_BASH:
            pytest.skip("Only runs on Windows with Git Bash")

        result = normalize_windows_path(r"cd C:\Users\test")
        assert result == "cd /c/Users/test"

    def test_quoted_path_with_spaces(self):
        """Test quoted path with spaces gets converted"""
        if not _IS_WINDOWS or not _USING_GIT_BASH:
            pytest.skip("Only runs on Windows with Git Bash")

        result = normalize_windows_path(r'"C:\Program Files\Git\bin\bash.exe"')
        assert result == '"/c/Program Files/Git/bin/bash.exe"'

    def test_url_not_converted(self):
        """Test that URLs are not converted"""
        if not _IS_WINDOWS or not _USING_GIT_BASH:
            pytest.skip("Only runs on Windows with Git Bash")

        result = normalize_windows_path(r"git clone https://github.com/foo/bar.git C:\temp")
        assert "https://github.com" in result
        assert "/c/temp" in result

    def test_multiple_paths_in_command(self):
        """Test command with multiple paths"""
        if not _IS_WINDOWS or not _USING_GIT_BASH:
            pytest.skip("Only runs on Windows with Git Bash")

        result = normalize_windows_path(r"cp C:\source\file.txt D:\dest\file.txt")
        assert result == "cp /c/source/file.txt /d/dest/file.txt"

    def test_backslashes_converted(self):
        """Test all backslashes are converted to forward slashes"""
        if not _IS_WINDOWS or not _USING_GIT_BASH:
            pytest.skip("Only runs on Windows with Git Bash")

        result = normalize_windows_path(r"ls C:\Users\test\Documents\Projects")
        assert "\\" not in result.split(":")[-1]  # No backslashes after drive letter
        assert result == "ls /c/Users/test/Documents/Projects"

    def test_mixed_paths(self):
        """Test command with both Unix and Windows paths"""
        if not _IS_WINDOWS or not _USING_GIT_BASH:
            pytest.skip("Only runs on Windows with Git Bash")

        result = normalize_windows_path(r"ls /tmp && ls C:\Windows")
        assert "/tmp" in result  # Unix path unchanged
        assert "/c/Windows" in result  # Windows path converted


class TestCrossPlatformBash:
    """Test that Bash tool works across all platforms"""

    def test_basic_echo(self):
        """Test basic echo command works on all platforms"""
        from tools import Bash

        tool = Bash(command='echo "Hello from CLI"')
        out = tool.run()
        assert "Exit code: 0" in out
        assert "Hello from CLI" in out

    def test_environment_detection(self):
        """Test that environment is correctly detected"""
        from tools.bash import _SYSTEM, _SHELL_TYPE

        assert _SYSTEM in ["Windows", "Darwin", "Linux"]
        assert _SHELL_TYPE in ["Git Bash", "PowerShell", "Bash"]

        # Verify it matches platform
        if platform.system() == "Windows":
            assert _SYSTEM == "Windows"
            assert _SHELL_TYPE in ["Git Bash", "PowerShell"]
        elif platform.system() == "Darwin":
            assert _SYSTEM == "Darwin"
            assert _SHELL_TYPE == "Bash"
        elif platform.system() == "Linux":
            assert _SYSTEM == "Linux"
            assert _SHELL_TYPE == "Bash"

    def test_working_directory_detection(self):
        """Test that working directory is correctly detected on all platforms"""
        from tools import Bash

        tool = Bash(command="pwd")
        out = tool.run()
        assert "Exit code: 0" in out

        # Should contain some path
        lines = out.split("\n")
        path_lines = [
            l for l in lines if l and "Exit code" not in l and "OUTPUT" not in l
        ]
        assert len(path_lines) > 0
