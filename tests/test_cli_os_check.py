import sys
import importlib
import pytest
from unittest.mock import patch

@pytest.mark.parametrize(
    "platform_str, release_str, should_exit",
    [
        ("linux", "5.15.0-73-generic", False),
        ("darwin", "22.6.0", False),
        # native Windows -> should exit
        ("win32", "11", True),
        # WSL -> should pass
        ("win32", "5.15.90.1-microsoft-standard-WSL2", False),
    ]
)
def test_cli_os_check(platform_str, release_str, should_exit):
    """Test the top-level OS check in clouddojo/cli.py"""
    
    with patch("sys.platform", platform_str), patch("platform.release", return_value=release_str):
        if "clouddojo.cli" in sys.modules:
            del sys.modules["clouddojo.cli"]

        if should_exit:
            with pytest.raises(SystemExit) as excinfo:
                importlib.import_module("clouddojo.cli")
            assert "CloudDojo CLI does not support Windows. Please use macOS, Linux, or WSL." in str(excinfo.value)
        else:
            importlib.import_module("clouddojo.cli")
