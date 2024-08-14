"""Fixtures for tests."""

from types import SimpleNamespace
import pytest
from wyoming_microsoft_tts.microsoft_tts import MicrosoftTTS
import os


@pytest.fixture
def configuration():
    """Return configuration."""
    return SimpleNamespace(
        subscription_key=os.environ.get("SPEECH_KEY"),
        service_region=os.environ.get("SPEECH_REGION"),
        voice="en-GB-SoniaNeural",
    )


@pytest.fixture
def microsoft_tts(configuration):
    """Return MicrosoftTTS instance."""
    return MicrosoftTTS(configuration)
