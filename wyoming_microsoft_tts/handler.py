"""Event handler for clients of the server."""

import argparse
import logging
from queue import Queue

from wyoming.audio import AudioChunk, AudioStart, AudioStop
from wyoming.event import Event
from wyoming.info import Describe, Info
from wyoming.server import AsyncEventHandler
from wyoming.tts import Synthesize

from .microsoft_tts import MicrosoftTTS

logging.basicConfig(format="%(asctime)s %(threadName)s %(message)s")
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

        rate = self.cli_args.sample_rate
        width = 2
        channels = 1
        queue = Queue[bytes]()
        _LOGGER.debug("Synthesizing (%dHz): %s", rate, text)

        try:
            await self.write_event(
                AudioStart(
                    rate=rate,
                    width=width,
                    channels=channels,
                ).event()
            )

            self.microsoft_tts.synthesize(text=text, voice=voice, bytes_queue=queue)

            while chunk := queue.get():
                if len(chunk) == 0:
                    _LOGGER.debug("Received empty chunk, stopping")
                    queue.task_done()
                    break

                await self.write_event(
                    AudioChunk(
                        audio=chunk,
                        rate=rate,
                        width=width,
                        channels=channels,
                    ).event()
                )
                queue.task_done()
                _LOGGER.debug("Sent audio chunk length %d", len(chunk))

            await self.write_event(AudioStop().event())
            _LOGGER.debug("Completed request")
        except Exception as e:
            _LOGGER.error("Failed to synthesize text: %s", e)
            return False

        return True
