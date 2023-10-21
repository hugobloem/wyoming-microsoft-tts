#!/usr/bin/env python3
import os, sys
import azure.cognitiveservices.speech as speechsdk
# from azure.cognitiveservices.speech.audio import AudioDataStream
import argparse
import json
from pathlib import Path
import time
import logging

parser = argparse.ArgumentParser()
parser.add_argument(
        "--service-region",
        required=True,
        help="Microsoft Azure region (e.g., westus2)",
)
parser.add_argument(
    "--subscription-key",
    required=True,
    help="Microsoft Azure subscription key",
)
parser.add_argument(
        "--voice",
        required=True,
        help="Default Microsoft voice to use (e.g., en_US-lessac-medium)",
)
parser.add_argument(
        "--json-input",
        action="store_true",
        help="Read input from stdin as JSON",
)
parser.add_argument(
        "--output-file",
        help="Write output to file instead of playing it",
)
parser.add_argument(
        "--output-dir",
        help="Write output to dir instead of playing it",
)
parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging",
)
args = parser.parse_args()

# log to file
log_file = Path(__file__).parent / "microsoft_tts.log"
logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG if args.debug else logging.INFO,
)
_LOGGER = logging.getLogger(__name__)
_LOGGER.debug("Starting script")

# This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
speech_config = speechsdk.SpeechConfig(subscription=args.subscription_key, region=args.service_region)
speech_config.speech_synthesis_voice_name=args.voice

if args.output_file:
    file_name = args.output_file
    audio_config = speechsdk.audio.AudioOutputConfig(filename=file_name)
elif args.output_dir:
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    file_name = output_dir / f"{time.monotonic_ns()}.wav"
    audio_config = speechsdk.audio.AudioOutputConfig(filename=str(file_name))
else:
    audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)

# The language of the voice that speaks.

speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

# Get text from the console and synthesize to the default speaker.
if args.json_input:
    _LOGGER.debug('Reading json')
    json_input = sys.stdin.read()
    text = json.loads(json_input)["text"]
    _LOGGER.debug('Received: %s'.format(text))
else:
    print("Type some text that you want to speak...")
    text = input()

speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()


if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
    _LOGGER.debug("Speech synthesized for text [{}]".format(text))

elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
    cancellation_details = speech_synthesis_result.cancellation_details
    _LOGGER.debug("Speech synthesis canceled: {}".format(cancellation_details.reason))
    if cancellation_details.reason == speechsdk.CancellationReason.Error:
        if cancellation_details.error_details:
            _LOGGER.debug("Error details: {}".format(cancellation_details.error_details))
            _LOGGER.debug("Did you set the speech resource key and region values?")