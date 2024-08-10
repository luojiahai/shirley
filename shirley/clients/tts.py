import azure.cognitiveservices.speech as speechsdk
import logging
import os
import pathlib
import sys
import uuid
from .client import Client
from typing import List


logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


class TextToSpeech(Client):

    def __init__(self, local: bool, *args, **kwargs) -> None:
        super().__init__(local=local)

        self._speech_key: str | None = os.environ.get('SPEECH_KEY')
        self._speech_region: str | None = os.environ.get('SPEECH_REGION')


    def get_available_locales(self) -> List[str]:
        locales = [
            'zh-CN',
            'zh-CN-henan',
            'zh-CN-liaoning',
            'zh-CN-shaanxi',
            'zh-CN-shandong',
            'zh-CN-sichuan',
            'zh-HK',
            'zh-TW',
            'wuu-CN',
            'yue-CN',
            'en-US',
            'en-AU',
        ]
        return locales


    def get_available_voices(self, locale: str) -> List[str] | None:
        if not self._speech_key or not self._speech_region:
            return None

        speech_config = speechsdk.SpeechConfig(subscription=self._speech_key, region=self._speech_region)
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)

        result: speechsdk.SynthesisVoicesResult = speech_synthesizer.get_voices_async(locale).get()
        if result.reason == speechsdk.ResultReason.VoicesListRetrieved:
            logger.info('Voices successfully retrieved')
            return [voice.short_name for voice in result.voices]
        elif result.reason == speechsdk.ResultReason.Canceled:
            logger.error(f'Speech synthesis canceled; error details: {result.error_details}')


    def text_to_speech(self, text: str, voice: str) -> pathlib.Path | None:
        if not self._speech_key or not self._speech_region:
            return None

        speech_config = speechsdk.SpeechConfig(subscription=self._speech_key, region=self._speech_region)
        speech_config.speech_synthesis_voice_name = voice
        speech_config.set_speech_synthesis_output_format(
            format_id=speechsdk.SpeechSynthesisOutputFormat.Riff24Khz16BitMonoPcm,
        )

        audios_tempdir = pathlib.Path(self.tempdir) / 'audios'
        audios_tempdir.mkdir(exist_ok=True, parents=True)
        name = f'audio-{uuid.uuid4()}.wav'
        filename = audios_tempdir / name
        audio_config = speechsdk.audio.AudioOutputConfig(filename=str(filename))

        speech_synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config,
            audio_config=audio_config,
        )

        speech_synthesis_result: speechsdk.SpeechSynthesisResult = speech_synthesizer.speak_text_async(text).get()

        if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            logger.info(f'Speech synthesized for text [{text}]')
            logger.info(f'Audio file saved in {str(filename)}.')
            return filename
        elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_synthesis_result.cancellation_details
            logger.error(f'Speech synthesis canceled: {cancellation_details.reason}')
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                if cancellation_details.error_details:
                    logger.error(f'Error details: {cancellation_details.error_details}')
                    logger.error('Did you set the speech resource key and region values?')
            return None
