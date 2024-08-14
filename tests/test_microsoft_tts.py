"""Tests for the MicrosoftTTS class."""


def test_initialize(microsoft_tts, configuration):
    """Test initialization."""
    assert microsoft_tts.args.voice == configuration["voice"]
    assert microsoft_tts.speech_config is not None
    assert microsoft_tts.output_dir is not None


def test_synthesize(microsoft_tts):
    """Test synthesize."""
    text = "Hello, world!"
    voice = "en-US-JennyNeural"

    result = microsoft_tts.synthesize(text, voice)
    assert result.endswith(".wav")
