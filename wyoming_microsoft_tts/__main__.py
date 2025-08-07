import argparse  # noqa: D100
import asyncio
import contextlib
import logging
import os
import signal
from functools import partial
from typing import Any

from wyoming.info import Attribution, Info, TtsProgram, TtsVoice
from wyoming.server import AsyncServer

from wyoming_microsoft_tts.download import get_voices
from wyoming_microsoft_tts.handler import MicrosoftEventHandler
from wyoming_microsoft_tts.version import __version__

_LOGGER = logging.getLogger(__name__)

stop_event = asyncio.Event()


def handle_stop_signal(*args):
    """Handle shutdown signal and set the stop event."""
    _LOGGER.info("Received stop signal. Shutting down...")
    stop_event.set()
    exit(0)


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--service-region",
        default=os.getenv("AZURE_SERVICE_REGION"),
        help="Microsoft Azure region (e.g., westus2)",
    )
    parser.add_argument(
        "--subscription-key",
        default=os.getenv("AZURE_SUBSCRIPTION_KEY"),
        help="Microsoft Azure subscription key",
    )
    parser.add_argument(
        "--voice",
        default="en-GB-SoniaNeural",
        help="Default Microsoft voice to use (e.g., en-GB-SoniaNeural)",
    )
    parser.add_argument(
        "--download-dir",
        default="/tmp/",
        type=str,
        help="Directory to download voices.json into (default: /tmp/)",
    )
    parser.add_argument(
        "--uri", default="tcp://0.0.0.0:10200", help="unix:// or tcp://"
    )
    #
    parser.add_argument(
        "--speaker", type=str, help="Name or id of speaker for default voice"
    )
    #
    parser.add_argument(
        "--auto-punctuation", default=".?!", help="Automatically add punctuation"
    )
    parser.add_argument(
        "--no-streaming",
        action="store_true",
        help="Disable audio streaming on sentence boundaries",
    )
    parser.add_argument("--samples-per-chunk", type=int, default=1024)
    #
    parser.add_argument(
        "--update-voices",
        action="store_true",
        help="Download latest voices.json during startup",
    )
    #
    parser.add_argument("--debug", action="store_true", help="Log DEBUG messages")
    return parser.parse_args()


def validate_args(args):
    """Validate command-line arguments."""
    if not args.service_region or not args.subscription_key:
        raise ValueError(
            "Both --service-region and --subscription-key must be provided either as command-line arguments or environment variables."
        )


async def main() -> None:
    """Start Wyoming Microsoft TTS server."""
    args = parse_arguments()
    validate_args(args)

    # setup logging
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)
    _LOGGER.debug("Arguments parsed successfully.")

    # Load voice info
    try:
        _LOGGER.info("Starting voices loading process.")
        voices_info = get_voices(
            args.download_dir,
            update_voices=args.update_voices,
            region=args.service_region,
            key=args.subscription_key,
        )
        _LOGGER.info("Voices loaded successfully.")
    except Exception as e:
        _LOGGER.error(f"Failed to load voices: {e}")
        return

    # Resolve aliases for backwards compatibility with old voice names
    aliases_info: dict[str, Any] = {}
    for voice_info in voices_info.values():
        for voice_alias in voice_info.get("aliases", []):
            aliases_info[voice_alias] = {"_is_alias": True, **voice_info}

    # Make sure default voice is in the list
    if args.voice not in voices_info:
        raise ValueError(
            f"Voice {args.voice} not found in voices.json, please look up the correct voice name here"
            + "\nhttps://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support?tabs=tts"
        )

    voices_info.update(aliases_info)
    voices = [
        TtsVoice(
            name=voice_name,
            description=get_description(voice_info),
            attribution=Attribution(
                name="Microsoft",
                url="https://github.com/hugobloem/wyoming-microsoft-tts",
            ),
            installed=True,
            version=__version__,
            languages=[
                voice_info.get("language", {}).get(
                    "code",
                    voice_info.get("espeak", {}).get("voice", voice_name.split("_")[0]),
                )
            ],
            #
            # Don't send speakers for now because it overflows StreamReader buffers
            # speakers=[
            #     TtsVoiceSpeaker(name=speaker_name)
            #     for speaker_name in voice_info["speaker_id_map"]
            # ]
            # if voice_info.get("speaker_id_map")
            # else None,
        )
        for voice_name, voice_info in voices_info.items()
        if not voice_info.get("_is_alias", False)
    ]

    wyoming_info = Info(
        tts=[
            TtsProgram(
                name="microsoft",
                description="A fast, local, neural text to speech engine",
                attribution=Attribution(
                    name="Microsoft",
                    url="https://github.com/hugobloem/wyoming-microsoft-tts",
                ),
                installed=True,
                version=__version__,
                voices=sorted(voices, key=lambda v: v.name),
                supports_synthesize_streaming=not args.no_streaming,
            )
        ],
    )

    # Start server
    server = AsyncServer.from_uri(args.uri)

    _LOGGER.info("Ready")
    try:
        await server.run(
            partial(
                MicrosoftEventHandler,
                wyoming_info,
                args,
            )
        )
    except Exception as e:
        _LOGGER.error(f"An error occurred while running the server: {e}")


# -----------------------------------------------------------------------------


def get_description(voice_info: dict[str, Any]):
    """Get a human readable description for a voice."""
    name = voice_info["name"]
    name = " ".join(name.split("_"))
    quality = voice_info["quality"]

    return f"{name} ({quality})"


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    # Set up signal handling for graceful shutdown
    signal.signal(signal.SIGTERM, handle_stop_signal)
    signal.signal(signal.SIGINT, handle_stop_signal)

    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(main())
