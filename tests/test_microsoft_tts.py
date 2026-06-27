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


# Per-Call SSML Fragment Tests


def test_ssml_detection_no_tags():
    """Test that plain text is not detected as SSML."""
    assert not MicrosoftTTS._has_ssml_tags("Hello, world!")
    assert not MicrosoftTTS._has_ssml_tags("x < 10 and y > 5")
    assert not MicrosoftTTS._has_ssml_tags("")


def test_ssml_detection_with_tags():
    """Test that SSML tags are correctly detected."""
    assert MicrosoftTTS._has_ssml_tags("<prosody rate='+50%'>hi</prosody>")
    assert MicrosoftTTS._has_ssml_tags("prefix <prosody>hi</prosody> suffix")
    assert MicrosoftTTS._has_ssml_tags("<mstts:express-as style='cheerful'>hi</mstts:express-as>")
    assert MicrosoftTTS._has_ssml_tags("<break time='100ms'/>")
    assert MicrosoftTTS._has_ssml_tags("<speak>hello</speak>")


def test_complete_ssml_passthrough():
    """Test that a complete SSML document is passed through as-is."""
    args = SimpleNamespace(
        subscription_key=None, service_region=None, download_dir="/tmp/",
        voice="en-US-JennyNeural", rate=None, pitch=None, volume=None,
        style=None, style_degree=None,
    )
    tts = MicrosoftTTS(args)
    ssml_doc = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis"'
        ' xml:lang="en-US">'
        '<voice name="en-US-JennyNeural">'
        'Hello, world!'
        '</voice>'
        '</speak>'
    )
    result = tts._build_ssml(ssml_doc, "en-US-JennyNeural")
    assert result == ssml_doc


def test_complete_ssml_passthrough_minimal():
    """Test that a minimal complete SSML (without XML declaration) passes through."""
    args = SimpleNamespace(
        subscription_key=None, service_region=None, download_dir="/tmp/",
        voice="en-US-JennyNeural", rate=None, pitch=None, volume=None,
        style=None, style_degree=None,
    )
    tts = MicrosoftTTS(args)
    ssml_doc = '<speak version="1.0"><voice name="x">hi</voice></speak>'
    result = tts._build_ssml(ssml_doc, "en-US-JennyNeural")
    assert result == ssml_doc


def test_fragment_prosody_merge():
    """Test server prosody defaults are injected into inline <prosody> tags."""
    args = SimpleNamespace(
        subscription_key=None, service_region=None, download_dir="/tmp/",
        voice="en-US-JennyNeural", rate="+30%", pitch="low", volume=None,
        style=None, style_degree=None,
    )
    tts = MicrosoftTTS(args)
    ssml = tts._build_ssml(
        '<prosody rate="+50%">fast</prosody>',
        "en-US-JennyNeural",
    )

    assert '<?xml version="1.0" encoding="UTF-8"?>' in ssml
    assert '<voice name="en-US-JennyNeural">' in ssml

    # Server defaults wrap the fragment (nested prosody)
    assert '<prosody rate="+30%" pitch="low">' in ssml
    # Inline prosody keeps its own rate, gets server pitch injected
    assert '<prosody rate="+50%" pitch="low">' in ssml or '<prosody pitch="low" rate="+50%">' in ssml
    assert "fast" in ssml
    assert '</prosody>' in ssml
    assert '</voice>' in ssml


def test_fragment_partial_prosody_override():
    """Test message attr overrides server default for same attr, missing attrs inherit."""
    args = SimpleNamespace(
        subscription_key=None, service_region=None, download_dir="/tmp/",
        voice="en-US-JennyNeural", rate="+30%", pitch="low", volume="+10%",
        style=None, style_degree=None,
    )
    tts = MicrosoftTTS(args)
    ssml = tts._build_ssml(
        '<prosody rate="+50%">partial override</prosody>',
        "en-US-JennyNeural",
    )

    # Middle wrapper has all server defaults
    assert '<prosody rate="+30%" pitch="low" volume="+10%">' in ssml
    # Inner overrides rate, gets pitch and volume from server
    assert 'rate="+50%"' in ssml
    assert 'pitch="low"' in ssml
    assert 'volume="+10%"' in ssml
    assert "partial override" in ssml


def test_fragment_style_merge():
    """Test server style defaults are injected into inline <mstts:express-as>."""
    args = SimpleNamespace(
        subscription_key=None, service_region=None, download_dir="/tmp/",
        voice="en-US-JennyNeural", rate=None, pitch=None, volume=None,
        style="cheerful", style_degree=None,
    )
    tts = MicrosoftTTS(args)
    ssml = tts._build_ssml(
        '<mstts:express-as style="sad">feeling sad</mstts:express-as>',
        "en-US-JennyNeural",
    )

    assert 'xmlns:mstts="https://www.w3.org/2001/mstts"' in ssml
    # Inline style overrides — should have style="sad" from message, NOT cheerful from server
    assert '<mstts:express-as style="sad">' in ssml or '<mstts:express-as style="sad">' in ssml
    assert "feeling sad" in ssml
    # No outer express-as wrapper since inline one exists
    assert ssml.count("mstts:express-as") == 2  # open + close


def test_fragment_style_with_degree_partial_override():
    """Test style_degree is injected when message only specifies style."""
    args = SimpleNamespace(
        subscription_key=None, service_region=None, download_dir="/tmp/",
        voice="en-US-JennyNeural", rate=None, pitch=None, volume=None,
        style="cheerful", style_degree=1.5,
    )
    tts = MicrosoftTTS(args)
    ssml = tts._build_ssml(
        '<mstts:express-as style="sad">mixed style</mstts:express-as>',
        "en-US-JennyNeural",
    )

    # style should be "sad" from message, styledegree should be "1.5" from server
    assert 'style="sad"' in ssml
    assert 'styledegree="1.5"' in ssml
    assert "mixed style" in ssml


def test_fragment_prosody_and_style():
    """Test both prosody and style fragments are merged correctly."""
    args = SimpleNamespace(
        subscription_key=None, service_region=None, download_dir="/tmp/",
        voice="en-US-JennyNeural", rate="fast", pitch=None, volume=None,
        style="excited", style_degree=1.2,
    )
    tts = MicrosoftTTS(args)
    ssml = tts._build_ssml(
        '<prosody rate="slow">dramatic pause</prosody>',
        "en-US-JennyNeural",
    )

    # Style wrapper from server (no inline style, so it gets added)
    assert '<mstts:express-as style="excited" styledegree="1.2">' in ssml
    # Prosody wrapper from server
    assert '<prosody rate="fast">' in ssml
    # Inner prosody overrides rate
    assert '<prosody rate="slow">' in ssml
    assert "dramatic pause" in ssml


def test_plain_text_without_server_defaults():
    """Test plain text without any server defaults stays plain text (no SSML wrapping)."""
    args = SimpleNamespace(
        subscription_key=None, service_region=None, download_dir="/tmp/",
        voice="en-US-JennyNeural", rate=None, pitch=None, volume=None,
        style=None, style_degree=None,
    )
    tts = MicrosoftTTS(args)
    ssml = tts._build_ssml("Hello, world!", "en-US-JennyNeural")

    # Plain text without CLI args goes through the plain SSML builder
    assert '<?xml version="1.0" encoding="UTF-8"?>' in ssml
    assert '<speak version="1.0"' in ssml
    assert '<voice name="en-US-JennyNeural">' in ssml
    assert 'Hello, world!' in ssml
    assert '<prosody' not in ssml
    assert '<mstts:express-as' not in ssml


def test_ssml_fragment_without_server_defaults():
    """Test SSML fragment is processed correctly even without any server defaults."""
    args = SimpleNamespace(
        subscription_key=None, service_region=None, download_dir="/tmp/",
        voice="en-US-JennyNeural", rate=None, pitch=None, volume=None,
        style=None, style_degree=None,
    )
    tts = MicrosoftTTS(args)
    ssml = tts._build_ssml(
        '<prosody rate="+50%">no server defaults</prosody>',
        "en-US-JennyNeural",
    )

    # No server prosody or style, so no wrapper should be added
    assert '<prosody rate="+50%">' in ssml
    assert "no server defaults" in ssml
    # No outer prosody wrapper since no server defaults
    # Inner prosody should be the only one (or none wrapping it)
    assert "xmlns:mstts" not in ssml


def test_invalid_xml_fragment_falls_back():
    """Test that text looking like SSML but with invalid XML falls back to plain text."""
    args = SimpleNamespace(
        subscription_key=None, service_region=None, download_dir="/tmp/",
        voice="en-US-JennyNeural", rate="+30%", pitch=None, volume=None,
        style=None, style_degree=None,
    )
    tts = MicrosoftTTS(args)
    # This has an unclosed tag, making it invalid XML
    ssml = tts._build_ssml(
        '<prosody rate="+50%">unclosed',
        "en-US-JennyNeural",
    )

    # Falls back to plain text wrapping with server defaults
    assert '<prosody rate="+30%">' in ssml
    assert "unclosed" in ssml


def test_mixed_ssml_fragment_with_plain_text():
    """Test fragment with inline prosody and surrounding plain text."""
    args = SimpleNamespace(
        subscription_key=None, service_region=None, download_dir="/tmp/",
        voice="en-US-JennyNeural", rate="+30%", pitch=None, volume=None,
        style=None, style_degree=None,
    )
    tts = MicrosoftTTS(args)
    ssml = tts._build_ssml(
        '<prosody rate="+50%">emphasized</prosody> normal text',
        "en-US-JennyNeural",
    )

    # Outer prosody wrapping everything
    assert '<prosody rate="+30%">' in ssml
    # Inner prosody with rate override + inherited from outer
    assert '<prosody rate="+50%">' in ssml
    assert "emphasized" in ssml
    assert "normal text" in ssml
    assert ssml.count('</prosody>') == 2  # inner + outer


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
