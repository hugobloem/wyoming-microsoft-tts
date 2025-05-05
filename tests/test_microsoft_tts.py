"""Tests for the MicrosoftTTS class."""

from queue import Queue


def test_initialize(microsoft_tts, configuration):
    """Test initialization."""
    assert microsoft_tts.args.voice == configuration["voice"]
    assert microsoft_tts.speech_config is not None


def test_synthesize(microsoft_tts):
    """Test synthesize."""
    text = "Hello, world!"
    voice = "en-US-JennyNeural"
    queue = Queue[bytes]()
    result = microsoft_tts.synthesize(text, bytes_queue=queue, voice=voice)
    assert result.get().audio_data is not None
    assert queue.qsize() > 0
