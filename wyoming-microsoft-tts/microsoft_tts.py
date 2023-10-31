import azure.cognitiveservices.speech as speechsdk
from pathlib import Path
import time
import logging
import tempfile

_LOGGER = logging.getLogger(__name__)

class MicrosoftTTS:
    def __init__(self, args) -> None:
        _LOGGER.debug("Initialize Microsoft TTS")
        self.args = args
        self.speech_config = speechsdk.SpeechConfig(subscription=args.subscription_key, region=args.service_region)

        output_dir = str(tempfile.TemporaryDirectory())
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir = output_dir

    def synthesize(self, text, voice=None):
        _LOGGER.debug("Requested TTS for [{}]".format(text))
        if voice is None:
            voice = self.args.voice

        self.speech_config.speech_synthesis_voice_name = voice

        file_name = self.output_dir / f"{time.monotonic_ns()}.wav"
        audio_config = speechsdk.audio.AudioOutputConfig(filename=str(file_name))

        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config, audio_config=audio_config)

        speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()

        if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            _LOGGER.debug("Speech synthesized for text [{}]".format(text))
            return str(file_name)

        elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_synthesis_result.cancellation_details
            _LOGGER.warning("Speech synthesis canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                _LOGGER.warning("Error details: {}".format(cancellation_details.error_details))
