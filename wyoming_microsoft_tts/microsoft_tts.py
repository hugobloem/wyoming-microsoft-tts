"""Microsoft TTS."""

import logging
import re
import tempfile
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import azure.cognitiveservices.speech as speechsdk

from .download import get_voices

_LOGGER = logging.getLogger(__name__)

_SSML_TAG_RE = re.compile(r"</?([\w:-]+)(?:\s[^>]*)?>")

ET.register_namespace("mstts", "https://www.w3.org/2001/mstts")


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

    @staticmethod
    def _has_ssml_tags(text: str) -> bool:
        """Check if text contains SSML markup tags."""
        return bool(_SSML_TAG_RE.search(text))

    @staticmethod
    def _is_complete_ssml(text: str) -> bool:
        """Check if text is a complete SSML document (starts with <speak or <?xml)."""
        stripped = text.strip()
        return stripped.startswith("<speak") or stripped.startswith("<?xml")

    def _build_ssml(self, text, voice):
        """Build SSML with prosody and style parameters.

        Handles three cases:
        1. Complete SSML document — passed through as-is
        2. SSML fragment — server defaults merged into inline tags
        3. Plain text — existing behavior (wraps with server defaults)
        """
        voice_key = self.voices[voice]["key"]
        voice_lang = self.voices[voice]["language"]["code"]

        if self._is_complete_ssml(text):
            return text

        if self._has_ssml_tags(text):
            merged = self._merge_ssml_fragment(text)
            if merged is not None:
                return self._build_ssml_structure(merged, voice_key, voice_lang)

        return self._build_ssml_plain(text, voice_key, voice_lang)

    def _merge_ssml_fragment(self, text: str) -> str | None:
        """Parse SSML fragment and merge server defaults into inline tags.

        For each <prosody> tag: injects server rate/pitch/volume for any
        attribute not already set on the tag.
        For each <mstts:express-as> tag: injects server style/style_degree
        for any attribute not already set on the tag.
        """
        try:
            wrapped = f'<root xmlns:mstts="https://www.w3.org/2001/mstts">{text}</root>'
            root = ET.fromstring(wrapped)
        except ET.ParseError:
            return None

        ns_mstts = "https://www.w3.org/2001/mstts"

        for elem in root.iter():
            if elem.tag == "prosody":
                if self.args.rate and "rate" not in elem.attrib:
                    elem.set("rate", self.args.rate)
                if self.args.pitch and "pitch" not in elem.attrib:
                    elem.set("pitch", self.args.pitch)
                if self.args.volume and "volume" not in elem.attrib:
                    elem.set("volume", self.args.volume)

            if elem.tag == f"{{{ns_mstts}}}express-as":
                if self.args.style and "style" not in elem.attrib:
                    elem.set("style", self.args.style)
                if self.args.style_degree is not None and "styledegree" not in elem.attrib:
                    elem.set("styledegree", str(self.args.style_degree))

        result = ET.tostring(root, encoding="unicode")
        close = result.index(">") + 1
        return result[close : -len("</root>")]

    def _get_style_attrs(self):
        """Build style attribute list from server args."""
        attrs = []
        if self.args.style is not None:
            attrs.append(f'style="{self.args.style}"')
        if self.args.style_degree is not None:
            attrs.append(f'styledegree="{self.args.style_degree}"')
        return attrs

    def _get_prosody_attrs(self):
        """Build prosody attribute list from server args."""
        attrs = []
        if self.args.rate:
            attrs.append(f'rate="{self.args.rate}"')
        if self.args.pitch:
            attrs.append(f'pitch="{self.args.pitch}"')
        if self.args.volume:
            attrs.append(f'volume="{self.args.volume}"')
        return attrs

    def _build_ssml_structure(self, inner_content, voice_key, voice_lang):
        """Wrap inner content in SSML structure with server-level defaults.

        The inner content may contain inline prosody/style tags that were
        already merged with server defaults. Server-level wrappers are added
        for attributes not covered inline:
        - <prosody> wrapper always added if server has rate/pitch/volume
          (Azure supports nested <prosody>; inner overrides outer per-attribute)
        - <mstts:express-as> wrapper added only if no inline style tag exists
        """
        has_style = self.args.style is not None or self.args.style_degree is not None
        has_prosody = any([self.args.rate, self.args.pitch, self.args.volume])
        has_inline_style = "<mstts:express-as" in inner_content

        parts = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis"',
        ]

        if has_style or has_inline_style:
            parts.append(' xmlns:mstts="https://www.w3.org/2001/mstts"')

        parts.append(f' xml:lang="{voice_lang}">')
        parts.append(f'<voice name="{voice_key}">')

        if has_style and not has_inline_style:
            style_attrs = self._get_style_attrs()
            parts.append(f'<mstts:express-as {" ".join(style_attrs)}>')

        if has_prosody:
            prosody_attrs = self._get_prosody_attrs()
            parts.append(f'<prosody {" ".join(prosody_attrs)}>')

        parts.append(inner_content)

        if has_prosody:
            parts.append("</prosody>")
        if has_style and not has_inline_style:
            parts.append("</mstts:express-as>")

        parts.append("</voice>")
        parts.append("</speak>")

        return "".join(parts)

    def _build_ssml_plain(self, text, voice_key, voice_lang):
        """Build SSML for plain text using only server-level defaults."""
        parts = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis"',
        ]

        if self.args.style or self.args.style_degree:
            parts.append(' xmlns:mstts="https://www.w3.org/2001/mstts"')

        parts.append(f' xml:lang="{voice_lang}">')
        parts.append(f'<voice name="{voice_key}">')

        has_style = self.args.style is not None
        has_prosody = any([self.args.rate, self.args.pitch, self.args.volume])

        if has_style:
            style_attrs = [f'style="{self.args.style}"']
            if self.args.style_degree is not None:
                style_attrs.append(f'styledegree="{self.args.style_degree}"')
            parts.append(f'<mstts:express-as {" ".join(style_attrs)}>')

        if has_prosody:
            prosody_attrs = []
            if self.args.rate:
                prosody_attrs.append(f'rate="{self.args.rate}"')
            if self.args.pitch:
                prosody_attrs.append(f'pitch="{self.args.pitch}"')
            if self.args.volume:
                prosody_attrs.append(f'volume="{self.args.volume}"')
            parts.append(f'<prosody {" ".join(prosody_attrs)}>')

        parts.append(text)

        if has_prosody:
            parts.append("</prosody>")

        if has_style:
            parts.append("</mstts:express-as>")

        parts.append("</voice>")
        parts.append("</speak>")

        return "".join(parts)

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

        if any([self.args.rate, self.args.pitch, self.args.volume, self.args.style, self.args.style_degree]) or self._has_ssml_tags(text):
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
