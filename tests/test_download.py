"""Tests for download functionality."""

import logging
import tempfile
from pathlib import Path
from unittest.mock import patch

from wyoming_microsoft_tts.download import get_voices


def test_get_voices_download_failure_logs_error(caplog):
    """Test that a failed download logs an error and continues with fallback."""
    with (
        tempfile.TemporaryDirectory() as temp_dir,
        patch("wyoming_microsoft_tts.download.urlopen") as mock_urlopen,
    ):
        mock_urlopen.side_effect = Exception("Network error")

        # Capture logs at error level
        with caplog.at_level(logging.ERROR):
            # Call get_voices with update_voices=True to trigger download
            voices = get_voices(
                download_dir=temp_dir,
                update_voices=True,
                region="westus",
                key="fake_key",
            )

        # Verify that we got an error log
        assert len(caplog.records) > 0
        error_logs = [
            record for record in caplog.records if record.levelname == "ERROR"
        ]
        assert len(error_logs) >= 1

        # Check that the error message is about failed update
        error_message = error_logs[0].message
        assert "Failed to update voices list" in error_message

        # Verify that voices are still returned (from embedded file)
        assert isinstance(voices, dict)
        assert len(voices) > 0  # Should have voices from embedded file


def test_get_voices_download_failure_uses_fallback():
    """Test that a failed download falls back to embedded voices."""
    with (
        tempfile.TemporaryDirectory() as temp_dir,
        patch("wyoming_microsoft_tts.download.urlopen") as mock_urlopen,
    ):
        mock_urlopen.side_effect = Exception("Network error")

        # Call get_voices with update_voices=True to trigger download
        voices = get_voices(
            download_dir=temp_dir, update_voices=True, region="westus", key="fake_key"
        )

        # Verify that voices are still returned from embedded file
        assert isinstance(voices, dict)
        assert len(voices) > 0

        # Verify that no downloaded file was created in temp directory
        download_path = Path(temp_dir) / "voices.json"
        assert not download_path.exists()


def test_get_voices_without_update_uses_embedded():
    """Test that get_voices works without update flag."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Call get_voices with update_voices=False (default)
        voices = get_voices(download_dir=temp_dir)

        # Should return voices from embedded file
        assert isinstance(voices, dict)
        assert len(voices) > 0
