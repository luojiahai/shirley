import azure.cognitiveservices.speech as speechsdk
import gradio as gr
import logging
import os
import pathlib
import shirley as sh
import sys
import uuid
from typing import Tuple


logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


class Speech(sh.Component):

    def __init__(self) -> None:
        super().__init__()

        speech_key = os.environ.get('SPEECH_KEY')
        speech_region = os.environ.get('SPEECH_REGION')

        self._speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
        self._speech_config.speech_synthesis_voice_name = 'zh-CN-XiaoxiaoNeural'
        self._speech_config.set_speech_synthesis_output_format(
            format_id=speechsdk.SpeechSynthesisOutputFormat.Riff24Khz16BitMonoPcm,
        )


    def _text_to_speech(self, text: str) -> pathlib.Path | None:
        images_tempdir = pathlib.Path(self.tempdir) / 'audio'
        images_tempdir.mkdir(exist_ok=True, parents=True)
        name = f'audio-{uuid.uuid4()}.wav'
        filename = images_tempdir / name
        audio_config = speechsdk.audio.AudioOutputConfig(filename=str(filename))

        speech_synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=self._speech_config,
            audio_config=audio_config,
        )

        speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()

        if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("Speech synthesized for text [{}]".format(text))
            return filename
        elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_synthesis_result.cancellation_details
            print("Speech synthesis canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                if cancellation_details.error_details:
                    print("Error details: {}".format(cancellation_details.error_details))
                    print("Did you set the speech resource key and region values?")
            return None


    def _convert(self, *args, **kwargs) -> sh.SpeechComponentsOutput:
        textbox: sh.TextboxInput = args[0]

        return self._text_to_speech(text=textbox)


    def _submit(self, *args, **kwargs) -> sh.SpeechComponentsOutput:
        textbox: sh.TextboxInput = args[0]

        if not textbox or not textbox.strip():
            raise gr.Error(visible=False)

        return None, textbox


    def _change(self, *args, **kwargs) -> sh.GradioComponents:
        textbox: sh.TextboxInput = args[0]

        if not textbox or not textbox.strip():
            return gr.Button(variant='secondary', interactive=False)

        return gr.Button(variant='primary', interactive=True)


    def _preconvert(self, *args, **kwargs) -> sh.GradioComponents:
        components = [
            gr.Textbox(interactive=False),
            gr.Button(variant='secondary', interactive=False),
        ]
        return components


    def _postconvert(self, *args, **kwargs) -> sh.GradioComponents:
        components = [
            gr.Textbox(interactive=True),
            gr.Button(variant='secondary', interactive=False),
        ]
        return components


    def _setup_textbox(self, *args, **kwargs) -> None:
        textbox: gr.Textbox = kwargs['textbox']
        convert_button: gr.Button = kwargs['convert_button']

        textbox.change(
            fn=self._change,
            inputs=[textbox],
            outputs=[convert_button],
            show_api=False,
        )


    def _setup_convert_button(self, *args, **kwargs) -> None:
        textbox: gr.Textbox = kwargs['textbox']
        text: gr.State = kwargs['text']
        convert_button: gr.Button = kwargs['convert_button']
        audio: gr.Audio = kwargs['audio']

        click = convert_button.click(
            fn=self._submit,
            inputs=[textbox],
            outputs=[textbox, text],
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
            inputs=[text],
            outputs=[audio],
            show_api=False,
        )
        convert.then(
            fn=self._postconvert,
            inputs=None,
            outputs=[textbox, convert_button],
            show_api=False,
        )


    def _setup(self, *args, **kwargs) -> None:
        self._setup_textbox(*args, **kwargs)
        self._setup_convert_button(*args, **kwargs)


    def make_components(self, *args, **kwargs) -> None:
        with gr.Row():
            with gr.Column():
                textbox = gr.Textbox(lines=10)
                text = gr.State('')
                convert_button = gr.Button(value='↪️ Convert (转换)', variant='secondary', interactive=False)
            with gr.Column():
                audio = gr.Audio(interactive=False)

        self._setup(
            textbox=textbox,
            text=text,
            convert_button=convert_button,
            audio=audio,
        )
