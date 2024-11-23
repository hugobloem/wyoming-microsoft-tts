"""Event handler for clients of the server."""

import argparse
import logging
import math
import os
import wave

from wyoming.audio import AudioChunk, AudioStart, AudioStop
from wyoming.event import Event
from wyoming.info import Describe, Info
from wyoming.server import AsyncEventHandler
from wyoming.tts import Synthesize

from .microsoft_tts import MicrosoftTTS

_LOGGER = logging.getLogger(__name__)


class MicrosoftEventHandler(AsyncEventHandler):
    """Event handler for clients of the server."""

    def __init__(
        self,
        wyoming_info: Info,
        cli_args: argparse.Namespace,
        *args,
        **kwargs,
    ) -> None:
        """Initialize."""
        super().__init__(*args, **kwargs)

        self.cli_args = cli_args
        self.wyoming_info_event = wyoming_info.event()
        self.microsoft_tts = MicrosoftTTS(cli_args)

    async def handle_event(self, event: Event) -> bool:
        """Handle an event."""
        if Describe.is_type(event.type):
            await self.write_event(self.wyoming_info_event)
            _LOGGER.debug("Sent info")
            return True

        if not Synthesize.is_type(event.type):
            _LOGGER.warning("Unexpected event: %s", event)
            return True

        synthesize = Synthesize.from_event(event)
        _LOGGER.debug(synthesize)

        raw_text = synthesize.text

        # Join multiple lines
        text = " ".join(raw_text.strip().splitlines())

        if synthesize.voice is None:  # Use default voice if not specified
            voice = self.cli_args.voice
        else:
            voice = synthesize.voice.name

        if self.cli_args.auto_punctuation and text:
            # Add automatic punctuation (important for some voices)
            has_punctuation = False
            for punc_char in self.cli_args.auto_punctuation:
                if text[-1] == punc_char:
                    has_punctuation = True
                    break

            if not has_punctuation:
                text = text + self.cli_args.auto_punctuation[0]

        _LOGGER.debug("Synthesizing: %s", text)
        try:
            output_path = self.microsoft_tts.synthesize(text=text, voice=voice)
        except Exception as e:
            _LOGGER.error("Failed to synthesize text: %s", e)
            return False

        _LOGGER.debug("Synthesized text")
        try:
            wav_file: wave.Wave_read = wave.open(output_path, "rb")
            with wav_file:
                rate = wav_file.getframerate()
                width = wav_file.getsampwidth()
                channels = wav_file.getnchannels()

                await self.write_event(
                    AudioStart(
                        rate=rate,
                        width=width,
                        channels=channels,
                    ).event(),
                )

                # Audio
                audio_bytes = wav_file.readframes(wav_file.getnframes())
                bytes_per_sample = width * channels
                bytes_per_chunk = bytes_per_sample * self.cli_args.samples_per_chunk
                num_chunks = int(math.ceil(len(audio_bytes) / bytes_per_chunk))

                # Split into chunks
                for i in range(num_chunks):
                    offset = i * bytes_per_chunk
                    chunk = audio_bytes[offset : offset + bytes_per_chunk]
                    await self.write_event(
                        AudioChunk(
                            audio=chunk,
                            rate=rate,
                            width=width,
                            channels=channels,
                        ).event(),
                    )
        except Exception as e:
            _LOGGER.error("Failed to send audio: %s", e)
            return False

        await self.write_event(AudioStop().event())
        _LOGGER.debug("Completed request")

        os.unlink(output_path)

        return True
