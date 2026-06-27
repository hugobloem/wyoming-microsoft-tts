"""Fixtures for tests."""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch
import pytest

# Mock azure SDK (not available on all platforms) before importing the module
import sys

sys.modules["azure"] = MagicMock()
sys.modules["azure.cognitiveservices"] = MagicMock()
sys.modules["azure.cognitiveservices.speech"] = MagicMock()

# Patch get_voices in download module to avoid network/voices.json dependency
voices_fake_data = {
    "en-US-JennyNeural": {
        "key": "en-US-JennyNeural",
        "language": {"code": "en-US"},
        "name": "Jenny",
    },
    "en-GB-SoniaNeural": {
        "key": "en-GB-SoniaNeural",
        "language": {"code": "en-GB"},
        "name": "Sonia",
    },
}


@pytest.fixture(autouse=True)
def patch_get_voices():
    """Patch get_voices to return known voices without network access."""
    with patch("wyoming_microsoft_tts.microsoft_tts.get_voices", return_value=voices_fake_data):
        yield


import os

from wyoming_microsoft_tts.microsoft_tts import MicrosoftTTS


@pytest.fixture
def configuration():
    """Return configuration."""
    return {
        "voice": "en-GB-SoniaNeural",
    }


@pytest.fixture
def microsoft_tts(configuration):
    """Return MicrosoftTTS instance."""
    args = SimpleNamespace(
        subscription_key=os.environ.get("SPEECH_KEY"),
        service_region=os.environ.get("SPEECH_REGION"),
        download_dir="/tmp/",
        rate=None,
        pitch=None,
        volume=None,
        style=None,
        style_degree=None,
        **configuration,
    )
    return MicrosoftTTS(args)
