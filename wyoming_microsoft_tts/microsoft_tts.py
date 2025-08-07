"""Microsoft TTS."""

import logging
from datetime import datetime
from queue import Queue

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

        if self.args.sample_rate == 8000:
            format = speechsdk.SpeechSynthesisOutputFormat.Raw8Khz16BitMonoPcm
        elif self.args.sample_rate == 16000:
            format = speechsdk.SpeechSynthesisOutputFormat.Raw16Khz16BitMonoPcm
        elif self.args.sample_rate == 22050:
            format = speechsdk.SpeechSynthesisOutputFormat.Raw22050Hz16BitMonoPcm
        elif self.args.sample_rate == 24000:
            format = speechsdk.SpeechSynthesisOutputFormat.Raw24Khz16BitMonoPcm
        elif self.args.sample_rate == 44100:
            format = speechsdk.SpeechSynthesisOutputFormat.Raw44100Hz16BitMonoPcm
        elif self.args.sample_rate == 48000:
            format = speechsdk.SpeechSynthesisOutputFormat.Raw48Khz16BitMonoPcm
        #
        else:
            format = speechsdk.SpeechSynthesisOutputFormat.Raw16Khz16BitMonoPcm

        self.speech_config.set_speech_synthesis_output_format(format)

        self.voices = get_voices(args.download_dir)

    def synthesize(
        self,
        text,
        bytes_queue: Queue[bytes],
        voice=None,
        language=None,
    ) -> speechsdk.ResultFuture:
        """Synthesize text to speech."""
        _LOGGER.debug(f"Requested TTS for [{text}]")
        if voice is None:
            voice = self.args.voice

        # Convert the requested voice to the key microsoft use.
        voice_name = self.voices[voice]["key"]
        language_code = self.voices[voice]["language"]["code"]

        class PushAudioOutputStreamCallbackQueue(
            speechsdk.audio.PushAudioOutputStreamCallback
        ):
            def __init__(
                self,
                queue: Queue[bytes],
            ):
                super().__init__()
                self.queue = queue

            def write(self, audio_buffer: memoryview) -> int:
                _LOGGER.debug(f"Got {len(audio_buffer)} bytes and pushing to queue")
                self.queue.put_nowait(audio_buffer.tobytes())
                return audio_buffer.nbytes

            def close(self) -> None:
                _LOGGER.debug("Stream closed")
                self.queue.put_nowait(b"")

        push_stream_queue = PushAudioOutputStreamCallbackQueue(bytes_queue)
        speech_synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=self.speech_config,
            audio_config=speechsdk.audio.AudioOutputConfig(
                stream=speechsdk.audio.PushAudioOutputStream(push_stream_queue)
            ),
        )

        # don't let it get collected while it's still running
        self._active_synthesizer = speech_synthesizer

        start = datetime.now()

        def result(evt: speechsdk.SpeechSynthesisEventArgs):
            result = evt.result
            push_stream_queue.close()

            speech_synthesizer.synthesis_canceled.disconnect_all()
            speech_synthesizer.synthesis_completed.disconnect_all()

            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                _LOGGER.debug(
                    f"{result.audio_duration} {round(len(result.audio_data)/1024, 1) }kB synthesized for text [{text}] in {(datetime.now() - start).total_seconds()} seconds"
                )
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = result.cancellation_details
                _LOGGER.warning(
                    f"Speech synthesis canceled: {cancellation_details.reason}"
                )
                if cancellation_details.reason == speechsdk.CancellationReason.Error:
                    _LOGGER.warning(
                        f"Error details: {cancellation_details.error_details}"
                    )

        speech_synthesizer.synthesis_completed.connect(result)
        speech_synthesizer.synthesis_canceled.connect(result)

        ssml = f"""
            <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="{language_code}">
                <voice name="{voice_name}">
                    <mstts:express-as style="assistant" styledegree="2">
                        {text}
                    </mstts:express-as>
                </voice>
            </speak>
        """

        return speech_synthesizer.speak_ssml_async(ssml)
