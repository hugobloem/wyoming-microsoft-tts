"""Fixtures for tests."""

from types import SimpleNamespace
import pytest
from wyoming_microsoft_tts.microsoft_tts import MicrosoftTTS


@pytest.fixture
def configuration():
    """Return configuration."""
    return SimpleNamespace(
        subscription_key="969acea67bd64af9b2c61e1b69703b29",
        service_region="uksouth",
        voice="en-GB-SoniaNeural",
    )


@pytest.fixture
def microsoft_tts(configuration):
    """Return MicrosoftTTS instance."""
    return MicrosoftTTS(configuration)
