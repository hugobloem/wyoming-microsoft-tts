"""Microsoft TTS."""

import logging
import tempfile
import time
from pathlib import Path

import azure.cognitiveservices.speech as speechsdk

from .download import get_voices

_LOGGER = logging.getLogger(__name__)


class MicrosoftTTS:
    """Class to handle Microsoft TTS."""

    def __init__(self, args) -> None:
        """Initialize."""
        _LOGGER.debug("Initialize Microsoft TTS")
        self.args = args
        self.speech_config = speechsdk.SpeechConfig(
            subscription=args.subscription_key, region=args.service_region
        )

        output_dir = str(tempfile.TemporaryDirectory())
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir = output_dir

        self.voices = get_voices(args.download_dir)

    def _build_ssml(self, text, voice):
        """Build SSML with prosody and style parameters."""
        voice_key = self.voices[voice]["key"]
        voice_lang = self.voices[voice]["language"]["code"]

        ssml_parts = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis"',
        ]

        if self.args.style or self.args.style_degree:
            ssml_parts.append(' xmlns:mstts="https://www.w3.org/2001/mstts"')

        ssml_parts.append(f' xml:lang="{voice_lang}">')
        ssml_parts.append(f'<voice name="{voice_key}">')

        has_style = self.args.style is not None
        has_prosody = any([self.args.rate, self.args.pitch, self.args.volume])

        if has_style:
            style_attrs = [f'style="{self.args.style}"']
            if self.args.style_degree is not None:
                style_attrs.append(f'styledegree="{self.args.style_degree}"')
            ssml_parts.append(f'<mstts:express-as {" ".join(style_attrs)}>')

        if has_prosody:
            prosody_attrs = []
            if self.args.rate:
                prosody_attrs.append(f'rate="{self.args.rate}"')
            if self.args.pitch:
                prosody_attrs.append(f'pitch="{self.args.pitch}"')
            if self.args.volume:
                prosody_attrs.append(f'volume="{self.args.volume}"')
            ssml_parts.append(f'<prosody {" ".join(prosody_attrs)}>')

        ssml_parts.append(text)

        if has_prosody:
            ssml_parts.append('</prosody>')

        if has_style:
            ssml_parts.append('</mstts:express-as>')

        ssml_parts.append('</voice>')
        ssml_parts.append('</speak>')

        return ''.join(ssml_parts)

    def synthesize(self, text, voice=None):
        """Synthesize text to speech."""
        _LOGGER.debug(f"Requested TTS for [{text}]")
        if voice is None:
            voice = self.args.voice

        # Convert the requested voice to the key microsoft use.
        self.speech_config.speech_synthesis_voice_name = self.voices[voice]["key"]

        file_name = self.output_dir / f"{time.monotonic_ns()}.wav"
        audio_config = speechsdk.audio.AudioOutputConfig(filename=str(file_name))

        speech_synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=self.speech_config, audio_config=audio_config
        )

        if any([self.args.rate, self.args.pitch, self.args.volume, self.args.style, self.args.style_degree]):
            ssml = self._build_ssml(text, voice)
            _LOGGER.debug(f"Using SSML: {ssml}")
            speech_synthesis_result = speech_synthesizer.speak_ssml_async(ssml).get()
        else:
            speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()

        if (
            speech_synthesis_result.reason
            == speechsdk.ResultReason.SynthesizingAudioCompleted
        ):
            _LOGGER.debug(f"Speech synthesized for text [{text}]")
            return str(file_name)

        elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_synthesis_result.cancellation_details
            _LOGGER.warning(f"Speech synthesis canceled: {cancellation_details.reason}")
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                _LOGGER.warning(f"Error details: {cancellation_details.error_details}")
