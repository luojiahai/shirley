
import gradio as gr
import logging
import shirley as sh
import sys
from .interface import Interface


logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


class TextToSpeech(Interface):

    def __init__(self, local: bool = False, *args, **kwargs) -> None:
        super().__init__()

        self._client = sh.clients.TextToSpeech(local=local)
        self._text: str = ''
        self._locale: str | None = None
        self._voice: str | None = None

        self._make_components(*args, **kwargs)


    @property
    def client(self) -> sh.clients.Chat:
        return self._client


    def _preconvert(self, *args, **kwargs) -> sh.types.GradioComponents:
        components = [
            gr.Textbox(interactive=False),
            gr.Button(variant='secondary', interactive=False),
            gr.ClearButton(interactive=False),
        ]
        return components


    def _convert(self, *args, **kwargs) -> sh.types.AudioOutput:
        return self._client.text_to_speech(text=self._text, voice=self._voice)


    def _postconvert(self, *args, **kwargs) -> sh.types.GradioComponents:
        components = [
            gr.Textbox(interactive=True),
            gr.Button(variant='primary', interactive=True),
            gr.ClearButton(interactive=True),
        ]
        return components


    def _submit(self, *args, **kwargs) -> None:
        textbox: sh.types.TextboxInput = args[0]

        if not textbox or not textbox.strip():
            raise gr.Error('Text not valid.')

        self._text = textbox


    def _reset(self, *args, **kwargs) -> sh.types.GradioComponents:
        self._text = ''

        return gr.Button(interactive=False)


    def _textbox_change(self, *args, **kwargs) -> sh.types.GradioComponents:
        textbox: sh.types.TextboxInput = args[0]

        if not textbox or not textbox.strip():
            return gr.Button(variant='secondary', interactive=False)

        self._text = textbox
        return gr.Button(variant='primary', interactive=True)


    def _locale_dropdown_change(self, *args, **kwargs) -> sh.types.GradioComponents:
        locale_dropdown: sh.types.DropdownInput = args[0]

        if not locale_dropdown or not locale_dropdown.strip():
            return gr.Dropdown(choices=None, interactive=False)

        self._locale = locale_dropdown
        voices = self._client.get_available_voices(locale=locale_dropdown)
        self._voice = None if not voices else voices[0]
        return gr.Dropdown(choices=voices, value=self._voice, interactive=True)


    def _voice_dropdown_change(self, *args, **kwargs) -> None:
        voice_dropdown: sh.types.DropdownInput = args[0]

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


    def _make_components(self, *args, **kwargs) -> None:
        locales = self._client.get_available_locales()
        self._locale = locales[0]
        voices = self._client.get_available_voices(locale=self._locale)
        self._voice = None if not voices else voices[0]

        with gr.Row():
            with gr.Column():
                textbox = gr.Textbox(
                    lines=16,
                    max_lines=16,
                    placeholder='✏️ Enter text… (输入文字…)',
                    show_label=False,
                    show_copy_button=True,
                )
                with gr.Row():
                    locale_dropdown = gr.Dropdown(
                        choices=locales,
                        value=self._locale,
                        multiselect=False,
                        allow_custom_value=False,
                        label='🌏 Locale (语言)',
                    )
                    voice_dropdown = gr.Dropdown(
                        choices=voices,
                        value=self._voice,
                        multiselect=False,
                        allow_custom_value=False,
                        label='🎤 Voice (声音)',
                    )
                with gr.Row():
                    convert_button = gr.Button(value='🔄 Convert (转换)', variant='secondary', interactive=False)
                    reset_button = gr.ClearButton(value='🧹 Reset (重置)', variant='secondary')

            with gr.Column():
                audio = gr.Audio(
                    type='filepath',
                    show_label=False,
                    scale=1,
                    interactive=False,
                    show_download_button=True,
                )

        self._setup(
            textbox=textbox,
            locale_dropdown=locale_dropdown,
            voice_dropdown=voice_dropdown,
            convert_button=convert_button,
            reset_button=reset_button,
            audio=audio,
        )
