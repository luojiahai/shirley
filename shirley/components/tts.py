import azure.cognitiveservices.speech as speechsdk
import gradio as gr
import logging
import os
import pathlib
import shirley as sh
import sys
import uuid
from typing import List, Tuple


logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


class TextToSpeechComponent(sh.Component):

    def __init__(self) -> None:
        super().__init__()
        self._speech_key: str | None = os.environ.get('SPEECH_KEY')
        self._speech_region: str | None = os.environ.get('SPEECH_REGION')
        self._text: str = ''
        self._locale: str | None = None
        self._voice: str | None = None


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

        result: speechsdk.SynthesisVoicesResult = speech_synthesizer.get_voices_async(locale).get()
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


    def _preconvert(self, *args, **kwargs) -> sh.GradioComponents:
        components = [
            gr.Textbox(interactive=False),
            gr.Button(variant='secondary', interactive=False),
            gr.ClearButton(interactive=False),
        ]
        return components


    def _convert(self, *args, **kwargs) -> sh.AudioOutput:
        return self._text_to_speech(text=self._text)


    def _postconvert(self, *args, **kwargs) -> sh.GradioComponents:
        components = [
            gr.Textbox(interactive=True),
            gr.Button(variant='primary', interactive=True),
            gr.ClearButton(interactive=True),
        ]
        return components


    def _submit(self, *args, **kwargs) -> None:
        textbox: sh.TextboxInput = args[0]

        if not textbox or not textbox.strip():
            raise gr.Error(visible=False)

        self._text = textbox


    def _reset(self, *args, **kwargs) -> sh.GradioComponents:
        self._text = ''

        return gr.Button(interactive=False)


    def _textbox_change(self, *args, **kwargs) -> sh.GradioComponents:
        textbox: sh.TextboxInput = args[0]

        if not textbox or not textbox.strip():
            return gr.Button(variant='secondary', interactive=False)

        self._text = textbox
        return gr.Button(variant='primary', interactive=True)


    def _locale_dropdown_change(self, *args, **kwargs) -> sh.GradioComponents:
        locale_dropdown: sh.DropdownInput = args[0]

        if not locale_dropdown or not locale_dropdown.strip():
            return gr.Dropdown(choices=None, interactive=False)

        self._locale = locale_dropdown
        voices = self._get_available_voices(locale=locale_dropdown)
        self._voice = voices[0]
        return gr.Dropdown(choices=voices, value=self._voice, interactive=True)


    def _voice_dropdown_change(self, *args, **kwargs) -> None:
        voice_dropdown: sh.DropdownInput = args[0]

        self._voice = voice_dropdown


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
        reset_button: gr.ClearButton = kwargs['reset_button']
        audio: gr.Audio = kwargs['audio']

        submit = convert_button.click(
            fn=self._submit,
            inputs=[textbox],
            outputs=None,
            show_api=False,
        )
        preconvert = submit.success(
            fn=self._preconvert,
            inputs=None,
            outputs=[textbox, convert_button, reset_button],
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
            outputs=[textbox, convert_button, reset_button],
            show_api=False,
        )


    def _setup_reset_button(self, *args, **kwargs) -> None:
        textbox: gr.Textbox = kwargs['textbox']
        convert_button: gr.Button = kwargs['convert_button']
        reset_button: gr.ClearButton = kwargs['reset_button']
        audio: gr.Audio = kwargs['audio']

        reset_button.add(components=[textbox, audio])

        reset_button.click(
            fn=self._reset,
            inputs=None,
            outputs=[convert_button],
            show_api=False,
        )


    def _setup(self, *args, **kwargs) -> None:
        self._setup_textbox(*args, **kwargs)
        self._setup_locale_dropdown(*args, **kwargs)
        self._setup_voice_dropdown(*args, **kwargs)
        self._setup_convert_button(*args, **kwargs)
        self._setup_reset_button(*args, **kwargs)


    def make_components(self, *args, **kwargs) -> None:
        gr.Markdown(value='### 🦈 Text-To-Speech')
        gr.Markdown(
            value='This is based on [Azure AI Speech](https://azure.microsoft.com/products/ai-services/ai-speech) \
            to implement text-to-speech functionality. \
            (此基于[Azure AI Speech](https://azure.microsoft.com/products/ai-services/ai-speech)打造，\
            实现文字转语音功能。)'
        )

        with gr.Row(variant='panel'):
            with gr.Column():
                textbox = gr.Textbox(
                    lines=16,
                    max_lines=16,
                    placeholder='✏️ Enter text… (输入文字…)',
                    label='🔤 Text (文字)',
                    show_copy_button=True,
                )
                with gr.Row():
                    locales = self._get_available_locales()
                    self._locale = locales[0]
                    locale_dropdown = gr.Dropdown(
                        choices=locales,
                        value=self._locale,
                        multiselect=False,
                        label='🌏 Locale (语言)',
                    )
                    voices = self._get_available_voices(locale=self._locale)
                    self._voice = voices[0]
                    voice_dropdown = gr.Dropdown(
                        choices=voices,
                        value=self._voice,
                        multiselect=False,
                        label='🎤 Voice (声音)',
                    )
                with gr.Row():
                    convert_button = gr.Button(value='🔄 Convert (转换)', variant='secondary', interactive=False)
                    reset_button = gr.ClearButton(value='🧹 Reset (重置)', variant='secondary')

            with gr.Column():
                audio = gr.Audio(
                    type='filepath',
                    label='🔊 Audio (语音)',
                    scale=1,
                    interactive=False,
                    show_download_button=True,
                )

        gr.Markdown(
            '<font size=2>Note: This is governed by the original license of Azure AI Speech. We strongly advise users \
            not to knowingly generate or allow others to knowingly generate harmful content, including hate speech, \
            violence, pornography, deception, etc. \
            (注：此受Azure AI Speech的许可协议限制。我们强烈建议，用户不应传播及不应允许他人传播以下内容，包括但不限于仇恨言论、\
            暴力、色情、欺诈相关的有害信息。)'
        )

        self._setup(
            textbox=textbox,
            locale_dropdown=locale_dropdown,
            voice_dropdown=voice_dropdown,
            convert_button=convert_button,
            reset_button=reset_button,
            audio=audio,
        )
