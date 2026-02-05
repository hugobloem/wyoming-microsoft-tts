"""Tests for the MicrosoftTTS class."""

from types import SimpleNamespace
import os
import pytest
from wyoming_microsoft_tts.microsoft_tts import MicrosoftTTS


def test_initialize(microsoft_tts, configuration):
    """Test initialization."""
    assert microsoft_tts.args.voice == configuration["voice"]
    assert microsoft_tts.speech_config is not None
    assert microsoft_tts.output_dir is not None


@pytest.mark.skipif(
    not os.environ.get("SPEECH_KEY") or not os.environ.get("SPEECH_REGION"),
    reason="SPEECH_KEY and SPEECH_REGION environment variables required",
)
def test_synthesize(microsoft_tts):
    """Test synthesize."""
    text = "Hello, world!"
    voice = "en-US-JennyNeural"

    result = microsoft_tts.synthesize(text, voice)
    assert result.endswith(".wav")


# SSML Building Tests


def test_build_ssml_with_rate():
    """Test SSML generation with rate parameter."""
    args = SimpleNamespace(
        subscription_key=os.environ.get("SPEECH_KEY"),
        service_region=os.environ.get("SPEECH_REGION"),
        download_dir="/tmp/",
        voice="en-US-JennyNeural",
        rate="+30%",
        pitch=None,
        volume=None,
        style=None,
        style_degree=None,
    )
    tts = MicrosoftTTS(args)
    ssml = tts._build_ssml("Hello, world!", "en-US-JennyNeural")

    assert '<?xml version="1.0" encoding="UTF-8"?>' in ssml
    assert '<speak version="1.0"' in ssml
    assert '<prosody rate="+30%">' in ssml
    assert "</prosody>" in ssml
    assert "Hello, world!" in ssml
    assert "xmlns:mstts" not in ssml  # No style, so no mstts namespace


def test_build_ssml_with_pitch():
    """Test SSML generation with pitch parameter."""
    args = SimpleNamespace(
        subscription_key=os.environ.get("SPEECH_KEY"),
        service_region=os.environ.get("SPEECH_REGION"),
        download_dir="/tmp/",
        voice="en-US-JennyNeural",
        rate=None,
        pitch="+10%",
        volume=None,
        style=None,
        style_degree=None,
    )
    tts = MicrosoftTTS(args)
    ssml = tts._build_ssml("Testing pitch", "en-US-JennyNeural")

    assert '<prosody pitch="+10%">' in ssml
    assert "</prosody>" in ssml
    assert "Testing pitch" in ssml


def test_build_ssml_with_volume():
    """Test SSML generation with volume parameter."""
    args = SimpleNamespace(
        subscription_key=os.environ.get("SPEECH_KEY"),
        service_region=os.environ.get("SPEECH_REGION"),
        download_dir="/tmp/",
        voice="en-US-JennyNeural",
        rate=None,
        pitch=None,
        volume="loud",
        style=None,
        style_degree=None,
    )
    tts = MicrosoftTTS(args)
    ssml = tts._build_ssml("Volume test", "en-US-JennyNeural")

    assert '<prosody volume="loud">' in ssml
    assert "</prosody>" in ssml
    assert "Volume test" in ssml


def test_build_ssml_with_all_prosody():
    """Test SSML generation with all prosody parameters."""
    args = SimpleNamespace(
        subscription_key=os.environ.get("SPEECH_KEY"),
        service_region=os.environ.get("SPEECH_REGION"),
        download_dir="/tmp/",
        voice="en-US-JennyNeural",
        rate="fast",
        pitch="high",
        volume="+20%",
        style=None,
        style_degree=None,
    )
    tts = MicrosoftTTS(args)
    ssml = tts._build_ssml("All prosody", "en-US-JennyNeural")

    assert '<prosody rate="fast" pitch="high" volume="+20%">' in ssml
    assert "</prosody>" in ssml
    assert "All prosody" in ssml


def test_build_ssml_with_style():
    """Test SSML generation with style parameter."""
    args = SimpleNamespace(
        subscription_key=os.environ.get("SPEECH_KEY"),
        service_region=os.environ.get("SPEECH_REGION"),
        download_dir="/tmp/",
        voice="en-US-JennyNeural",
        rate=None,
        pitch=None,
        volume=None,
        style="cheerful",
        style_degree=None,
    )
    tts = MicrosoftTTS(args)
    ssml = tts._build_ssml("Style test", "en-US-JennyNeural")

    assert 'xmlns:mstts="https://www.w3.org/2001/mstts"' in ssml
    assert '<mstts:express-as style="cheerful">' in ssml
    assert "</mstts:express-as>" in ssml
    assert "Style test" in ssml


def test_build_ssml_with_style_and_degree():
    """Test SSML generation with style and style_degree parameters."""
    args = SimpleNamespace(
        subscription_key=os.environ.get("SPEECH_KEY"),
        service_region=os.environ.get("SPEECH_REGION"),
        download_dir="/tmp/",
        voice="en-US-JennyNeural",
        rate=None,
        pitch=None,
        volume=None,
        style="sad",
        style_degree=1.5,
    )
    tts = MicrosoftTTS(args)
    ssml = tts._build_ssml("Sad voice", "en-US-JennyNeural")

    assert 'xmlns:mstts="https://www.w3.org/2001/mstts"' in ssml
    assert '<mstts:express-as style="sad" styledegree="1.5">' in ssml
    assert "</mstts:express-as>" in ssml
    assert "Sad voice" in ssml


def test_build_ssml_with_prosody_and_style():
    """Test SSML generation with both prosody and style parameters."""
    args = SimpleNamespace(
        subscription_key=os.environ.get("SPEECH_KEY"),
        service_region=os.environ.get("SPEECH_REGION"),
        download_dir="/tmp/",
        voice="en-US-JennyNeural",
        rate="slow",
        pitch="low",
        volume="soft",
        style="calm",
        style_degree=0.5,
    )
    tts = MicrosoftTTS(args)
    ssml = tts._build_ssml("Combined test", "en-US-JennyNeural")

    assert 'xmlns:mstts="https://www.w3.org/2001/mstts"' in ssml
    assert '<mstts:express-as style="calm" styledegree="0.5">' in ssml
    assert '<prosody rate="slow" pitch="low" volume="soft">' in ssml
    assert "</prosody>" in ssml
    assert "</mstts:express-as>" in ssml
    assert "Combined test" in ssml


def test_build_ssml_voice_key_and_lang():
    """Test that SSML uses correct voice key and language."""
    args = SimpleNamespace(
        subscription_key=os.environ.get("SPEECH_KEY"),
        service_region=os.environ.get("SPEECH_REGION"),
        download_dir="/tmp/",
        voice="en-GB-SoniaNeural",
        rate="+10%",
        pitch=None,
        volume=None,
        style=None,
        style_degree=None,
    )
    tts = MicrosoftTTS(args)
    ssml = tts._build_ssml("UK voice", "en-GB-SoniaNeural")

    # Should contain the voice key from the voices.json
    assert 'xml:lang="en-GB"' in ssml
    assert '<voice name="en-GB-SoniaNeural">' in ssml


# Integration Tests with Synthesize


@pytest.mark.skipif(
    not os.environ.get("SPEECH_KEY") or not os.environ.get("SPEECH_REGION"),
    reason="SPEECH_KEY and SPEECH_REGION environment variables required",
)
def test_synthesize_with_rate():
    """Test synthesize with rate parameter."""
    args = SimpleNamespace(
        subscription_key=os.environ.get("SPEECH_KEY"),
        service_region=os.environ.get("SPEECH_REGION"),
        download_dir="/tmp/",
        voice="en-US-JennyNeural",
        rate="+30%",
        pitch=None,
        volume=None,
        style=None,
        style_degree=None,
    )
    tts = MicrosoftTTS(args)
    result = tts.synthesize("Testing rate parameter", "en-US-JennyNeural")

    assert result is not None
    assert result.endswith(".wav")


@pytest.mark.skipif(
    not os.environ.get("SPEECH_KEY") or not os.environ.get("SPEECH_REGION"),
    reason="SPEECH_KEY and SPEECH_REGION environment variables required",
)
def test_synthesize_with_pitch():
    """Test synthesize with pitch parameter."""
    args = SimpleNamespace(
        subscription_key=os.environ.get("SPEECH_KEY"),
        service_region=os.environ.get("SPEECH_REGION"),
        download_dir="/tmp/",
        voice="en-US-JennyNeural",
        rate=None,
        pitch="+5%",
        volume=None,
        style=None,
        style_degree=None,
    )
    tts = MicrosoftTTS(args)
    result = tts.synthesize("Testing pitch parameter", "en-US-JennyNeural")

    assert result is not None
    assert result.endswith(".wav")


@pytest.mark.skipif(
    not os.environ.get("SPEECH_KEY") or not os.environ.get("SPEECH_REGION"),
    reason="SPEECH_KEY and SPEECH_REGION environment variables required",
)
def test_synthesize_with_volume():
    """Test synthesize with volume parameter."""
    args = SimpleNamespace(
        subscription_key=os.environ.get("SPEECH_KEY"),
        service_region=os.environ.get("SPEECH_REGION"),
        download_dir="/tmp/",
        voice="en-US-JennyNeural",
        rate=None,
        pitch=None,
        volume="loud",
        style=None,
        style_degree=None,
    )
    tts = MicrosoftTTS(args)
    result = tts.synthesize("Testing volume parameter", "en-US-JennyNeural")

    assert result is not None
    assert result.endswith(".wav")


@pytest.mark.skipif(
    not os.environ.get("SPEECH_KEY") or not os.environ.get("SPEECH_REGION"),
    reason="SPEECH_KEY and SPEECH_REGION environment variables required",
)
def test_synthesize_with_style():
    """Test synthesize with style parameter."""
    args = SimpleNamespace(
        subscription_key=os.environ.get("SPEECH_KEY"),
        service_region=os.environ.get("SPEECH_REGION"),
        download_dir="/tmp/",
        voice="en-US-JennyNeural",
        rate=None,
        pitch=None,
        volume=None,
        style="cheerful",
        style_degree=None,
    )
    tts = MicrosoftTTS(args)
    result = tts.synthesize("Testing style parameter", "en-US-JennyNeural")

    assert result is not None
    assert result.endswith(".wav")


@pytest.mark.skipif(
    not os.environ.get("SPEECH_KEY") or not os.environ.get("SPEECH_REGION"),
    reason="SPEECH_KEY and SPEECH_REGION environment variables required",
)
def test_synthesize_with_combined_parameters():
    """Test synthesize with multiple parameters combined."""
    args = SimpleNamespace(
        subscription_key=os.environ.get("SPEECH_KEY"),
        service_region=os.environ.get("SPEECH_REGION"),
        download_dir="/tmp/",
        voice="en-US-JennyNeural",
        rate="fast",
        pitch="+10%",
        volume="loud",
        style="excited",
        style_degree=1.2,
    )
    tts = MicrosoftTTS(args)
    result = tts.synthesize("Testing all parameters together", "en-US-JennyNeural")

    assert result is not None
    assert result.endswith(".wav")


@pytest.mark.skipif(
    not os.environ.get("SPEECH_KEY") or not os.environ.get("SPEECH_REGION"),
    reason="SPEECH_KEY and SPEECH_REGION environment variables required",
)
def test_synthesize_without_parameters_still_works():
    """Test that synthesize still works without any new parameters."""
    args = SimpleNamespace(
        subscription_key=os.environ.get("SPEECH_KEY"),
        service_region=os.environ.get("SPEECH_REGION"),
        download_dir="/tmp/",
        voice="en-US-JennyNeural",
        rate=None,
        pitch=None,
        volume=None,
        style=None,
        style_degree=None,
    )
    tts = MicrosoftTTS(args)
    result = tts.synthesize("Testing without parameters", "en-US-JennyNeural")

    assert result is not None
    assert result.endswith(".wav")
