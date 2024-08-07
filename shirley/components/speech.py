import azure.cognitiveservices.speech as speechsdk
import gradio as gr
import logging
import os
import pathlib
import shirley as sh
import sys
import uuid
from typing import List


logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


class SpeechComponent(sh.Component):

    def __init__(self) -> None:
        super().__init__()
        self._speech_key = os.environ.get('SPEECH_KEY')
        self._speech_region = os.environ.get('SPEECH_REGION')
        self._text = ''
        self._locale = 'zh-CN'
        self._voice = 'zh-CN-XiaoxiaoNeural'


    def _get_available_locales(self) -> List[str]:
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


    def _get_available_voices(self, locale: str) -> List[str]:
        speech_config = speechsdk.SpeechConfig(subscription=self._speech_key, region=self._speech_region)
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)

        result = speech_synthesizer.get_voices_async(locale).get()
        if result.reason == speechsdk.ResultReason.VoicesListRetrieved:
            logger.info('Voices successfully retrieved')
            return [voice.short_name for voice in result.voices]
        elif result.reason == speechsdk.ResultReason.Canceled:
            logger.error(f'Speech synthesis canceled; error details: {result.error_details}')


    def _text_to_speech(self, text: str) -> pathlib.Path | None:
        speech_config = speechsdk.SpeechConfig(subscription=self._speech_key, region=self._speech_region)
        speech_config.speech_synthesis_voice_name = self._voice
        speech_config.set_speech_synthesis_output_format(
            format_id=speechsdk.SpeechSynthesisOutputFormat.Riff24Khz16BitMonoPcm,
        )

        images_tempdir = pathlib.Path(self.tempdir) / 'audio'
        images_tempdir.mkdir(exist_ok=True, parents=True)
        name = f'audio-{uuid.uuid4()}.wav'
        filename = images_tempdir / name
        audio_config = speechsdk.audio.AudioOutputConfig(filename=str(filename))

        speech_synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config,
            audio_config=audio_config,
        )

        speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()

        if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            logger.info(f'Speech synthesized for text [{text}]')
            return filename
        elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_synthesis_result.cancellation_details
            logger.error(f'Speech synthesis canceled: {cancellation_details.reason}')
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                if cancellation_details.error_details:
                    logger.error(f'Error details: {cancellation_details.error_details}')
                    logger.error('Did you set the speech resource key and region values?')
            return None


    def _preconvert(self, *args, **kwargs) -> sh.GradioComponents:
        components = [
            gr.Textbox(interactive=False),
            gr.Button(variant='secondary', interactive=False),
        ]
        return components


    def _convert(self, *args, **kwargs) -> sh.SpeechComponentsOutput:
        return self._text_to_speech(text=self._text)


    def _postconvert(self, *args, **kwargs) -> sh.GradioComponents:
        components = [
            gr.Textbox(interactive=True),
            gr.Button(variant='primary', interactive=True),
        ]
        return components


    def _submit(self, *args, **kwargs) -> sh.SpeechComponentsOutput:
        textbox: sh.TextboxInput = args[0]

        if not textbox or not textbox.strip():
            raise gr.Error(visible=False)

        self._text = textbox


    def _reset(self, *args, **kwargs) -> sh.GradioComponents:
        return gr.Button(interactive=False)


    def _textbox_change(self, *args, **kwargs) -> sh.GradioComponents:
        textbox: sh.TextboxInput = args[0]

        if not textbox or not textbox.strip():
            return gr.Button(variant='secondary', interactive=False)

        self._text = textbox
        return gr.Button(variant='primary', interactive=True)


    def _locale_dropdown_change(self, *args, **kwargs) -> sh.GradioComponents:
        locale_dropdown: sh.LocaleDropdownInput = args[0]

        if not locale_dropdown or not locale_dropdown.strip():
            return gr.Dropdown(choices=None, interactive=False)

        self._locale = locale_dropdown
        return gr.Dropdown(choices=self._get_available_voices(locale=locale_dropdown), interactive=True)


    def _voice_dropdown_change(self, *args, **kwargs) -> sh.GradioComponents:
        voice_dropdown: sh.LocaleDropdownInput = args[0]

        self._voice = voice_dropdown


    def _reset_button_click(self, *args, **kwargs) -> sh.SpeechComponentsOutput:
        self._text = ''
        self._locale = 'zh-CN'
        self._voice = 'zh-CN-XiaoxiaoNeural'

        return None, None


    def _setup_textbox(self, *args, **kwargs) -> None:
        textbox: gr.Textbox = kwargs['textbox']
        convert_button: gr.Button = kwargs['convert_button']

        textbox.change(
            fn=self._textbox_change,
            inputs=[textbox],
            outputs=[convert_button],
            show_api=False,
        )


    def _setup_locale_dropdown(self, *args, **kwargs) -> None:
        locale_dropdown: gr.Dropdown = kwargs['locale_dropdown']
        voice_dropdown: gr.Dropdown = kwargs['voice_dropdown']

        locale_dropdown.change(
            fn=self._locale_dropdown_change,
            inputs=[locale_dropdown],
            outputs=[voice_dropdown],
            show_api=False,
        )


    def _setup_voice_dropdown(self, *args, **kwargs) -> None:
        voice_dropdown: gr.Dropdown = kwargs['voice_dropdown']

        voice_dropdown.change(
            fn=self._voice_dropdown_change,
            inputs=[voice_dropdown],
            outputs=None,
            show_api=False,
        )


    def _setup_convert_button(self, *args, **kwargs) -> None:
        textbox: gr.Textbox = kwargs['textbox']
        convert_button: gr.Button = kwargs['convert_button']
        audio: gr.Audio = kwargs['audio']

        click = convert_button.click(
            fn=self._submit,
            inputs=[textbox],
            outputs=None,
            show_api=False,
        )
        preconvert = click.success(
            fn=self._preconvert,
            inputs=None,
            outputs=[textbox, convert_button],
            show_api=False,
        )
        convert = preconvert.then(
            fn=self._convert,
            inputs=None,
            outputs=[audio],
            show_api=False,
        )
        convert.then(
            fn=self._postconvert,
            inputs=None,
            outputs=[textbox, convert_button],
            show_api=False,
        )


    def _setup_reset_button(self, *args, **kwargs):
        textbox: gr.Textbox = kwargs['textbox']
        convert_button: gr.Button = kwargs['convert_button']
        reset_button: gr.Button = kwargs['reset_button']
        audio: gr.Audio = kwargs['audio']

        reset_button_click = reset_button.click(
            fn=self._reset_button_click,
            inputs=None,
            outputs=[textbox, audio]
        )
        reset_button_click.then(
            fn=self._reset,
            inputs=None,
            outputs=[convert_button]
        )


    def _setup(self, *args, **kwargs) -> None:
        self._setup_textbox(*args, **kwargs)
        self._setup_locale_dropdown(*args, **kwargs)
        self._setup_voice_dropdown(*args, **kwargs)
        self._setup_convert_button(*args, **kwargs)
        self._setup_reset_button(*args, **kwargs)


    def make_components(self, *args, **kwargs) -> None:
        gr.Markdown(value='### 🦈 Text-To-Speech')
        with gr.Row():
            with gr.Column():
                textbox = gr.Textbox(lines=10)
                with gr.Row():
                    locale_dropdown = gr.Dropdown(
                        choices=self._get_available_locales(),
                        value=self._locale,
                        multiselect=False,
                        label='🌏 Locale (语言)',
                    )
                    voices = self._get_available_voices(locale=self._locale)
                    voice_dropdown = gr.Dropdown(
                        choices=voices,
                        value=voices[0],
                        multiselect=False,
                        label='🎤 Voice (声音)',
                    )
                with gr.Row():
                    convert_button = gr.Button(value='↪️ Convert (转换)', variant='secondary', interactive=False)
                    reset_button = gr.Button(value='🧹 Reset (重置)', variant='secondary')
            with gr.Column():
                audio = gr.Audio(interactive=False)

        self._setup(
            textbox=textbox,
            locale_dropdown=locale_dropdown,
            voice_dropdown=voice_dropdown,
            convert_button=convert_button,
            reset_button=reset_button,
            audio=audio,
        )
