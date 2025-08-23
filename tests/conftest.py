"""Fixtures for tests."""

from types import SimpleNamespace
import pytest
from wyoming_microsoft_tts.microsoft_tts import MicrosoftTTS
import os


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
        **configuration,
    )
    return MicrosoftTTS(args)
