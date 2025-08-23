"""Tests for voice parsing functionality."""

import json
from io import StringIO


from wyoming_microsoft_tts.download import transform_voices_files


def test_voice_parsing_with_script_codes():
    """Test that voices with script codes in locales are parsed correctly."""
    # Sample Microsoft API response with problematic locales
    sample_response = [
        {
            "ShortName": "iu-Cans-CA-SiqiniqNeural",
            "Locale": "iu-Cans-CA",
            "LocalName": "Siqiniq",
            "LocaleName": "Inuktitut (Canadian Aboriginal Syllabics, Canada)",
            "VoiceType": "Neural",
        },
        {
            "ShortName": "iu-Latn-CA-TaqqiqNeural",
            "Locale": "iu-Latn-CA",
            "LocalName": "Taqqiq",
            "LocaleName": "Inuktitut (Latin, Canada)",
            "VoiceType": "Neural",
        },
        {
            "ShortName": "sr-Latn-RS-NicholasNeural",
            "Locale": "sr-Latn-RS",
            "LocalName": "Nicholas",
            "LocaleName": "Serbian (Latin, Serbia)",
            "VoiceType": "Neural",
        },
        {
            "ShortName": "en-US-JennyNeural",
            "Locale": "en-US",
            "LocalName": "Jenny",
            "LocaleName": "English (United States)",
            "VoiceType": "Neural",
        },
    ]

    # Create a StringIO object to simulate the API response
    response_io = StringIO(json.dumps(sample_response))

    # Transform the voices
    voices = transform_voices_files(response_io)

    # Verify that all voices were processed successfully
    assert len(voices) == 4, f"Expected 4 voices, got {len(voices)}"

    # Check that the problematic voices are included
    assert "iu-Cans-CA-SiqiniqNeural" in voices
    assert "iu-Latn-CA-TaqqiqNeural" in voices
    assert "sr-Latn-RS-NicholasNeural" in voices
    assert "en-US-JennyNeural" in voices

    # Check that the voice data is properly structured
    for _voice_name, voice_data in voices.items():
        assert "key" in voice_data
        assert "name" in voice_data
        assert "language" in voice_data
        assert "quality" in voice_data
        assert "region" in voice_data["language"]
        assert "country_english" in voice_data["language"]

        # Verify that region and country_english are not None
        assert voice_data["language"]["region"] is not None
        assert voice_data["language"]["country_english"] is not None


def test_voice_parsing_with_secondary_locales():
    """Test that voices with secondary locales are parsed correctly."""
    sample_response = [
        {
            "ShortName": "en-US-JennyMultilingualNeural",
            "Locale": "en-US",
            "LocalName": "Jenny",
            "LocaleName": "English (United States)",
            "VoiceType": "Neural",
            "SecondaryLocaleList": ["de-DE", "es-ES"],
        }
    ]

    response_io = StringIO(json.dumps(sample_response))
    voices = transform_voices_files(response_io)

    # Should have 3 voices: original + 2 secondary locales
    assert len(voices) == 3
    assert "en-US-JennyMultilingualNeural" in voices
    assert "de-DE-JennyMultilingualNeural" in voices
    assert "es-ES-JennyMultilingualNeural" in voices


def test_voice_parsing_with_standard_locales():
    """Test that standard locale format (lang-COUNTRY) still works correctly."""
    sample_response = [
        {
            "ShortName": "en-US-JennyNeural",
            "Locale": "en-US",
            "LocalName": "Jenny",
            "LocaleName": "English (United States)",
            "VoiceType": "Neural",
        },
        {
            "ShortName": "fr-FR-DeniseNeural",
            "Locale": "fr-FR",
            "LocalName": "Denise",
            "LocaleName": "French (France)",
            "VoiceType": "Neural",
        },
        {
            "ShortName": "de-DE-KatjaNeural",
            "Locale": "de-DE",
            "LocalName": "Katja",
            "LocaleName": "German (Germany)",
            "VoiceType": "Neural",
        },
    ]

    response_io = StringIO(json.dumps(sample_response))
    voices = transform_voices_files(response_io)

    # Should have all 3 voices
    assert len(voices) == 3

    # Check country mappings are correct for standard locales
    assert voices["en-US-JennyNeural"]["language"]["region"] == "US"
    assert voices["en-US-JennyNeural"]["language"]["country_english"] == "United States"

    assert voices["fr-FR-DeniseNeural"]["language"]["region"] == "FR"
    assert voices["fr-FR-DeniseNeural"]["language"]["country_english"] == "France"

    assert voices["de-DE-KatjaNeural"]["language"]["region"] == "DE"
    assert voices["de-DE-KatjaNeural"]["language"]["country_english"] == "Germany"


def test_voice_parsing_with_invalid_locales():
    """Test that voices with completely invalid locales use fallback values."""
    sample_response = [
        {
            "ShortName": "xx-INVALID-TestNeural",
            "Locale": "xx-INVALID",
            "LocalName": "Test",
            "LocaleName": "Test Language",
            "VoiceType": "Neural",
        },
        {
            "ShortName": "yy-ZZ-FAKE-TestNeural",
            "Locale": "yy-ZZ-FAKE",
            "LocalName": "Test2",
            "LocaleName": "Test Language 2",
            "VoiceType": "Neural",
        },
    ]

    response_io = StringIO(json.dumps(sample_response))
    voices = transform_voices_files(response_io)

    # Should have both voices with fallback values
    assert len(voices) == 2

    # Check fallback values are used
    assert voices["xx-INVALID-TestNeural"]["language"]["region"] == "INVALID"
    assert voices["xx-INVALID-TestNeural"]["language"]["country_english"] == "Unknown"

    assert voices["yy-ZZ-FAKE-TestNeural"]["language"]["region"] == "FAKE"
    assert voices["yy-ZZ-FAKE-TestNeural"]["language"]["country_english"] == "Unknown"
