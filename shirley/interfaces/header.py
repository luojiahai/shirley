import gradio as gr
import logging
import sys
from .interface import Interface
from shirley.options import HeaderInterfaceOptions


logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


class Header(Interface):

    def __init__(self, options: HeaderInterfaceOptions = HeaderInterfaceOptions()) -> None:
        super().__init__(options=options)

        self._make_components(options=options)


    def _setup_dark_mode_button(self, *args, **kwargs) -> None:
        dark_mode_button: gr.Button = kwargs['dark_mode_button']

        dark_mode_button.click(
            fn=None,
            js='() => { document.body.classList.toggle(\'dark\'); }',
            show_api=False,
        )


    def _setup(self, *args, **kwargs) -> None:
        self._setup_dark_mode_button(*args, **kwargs)


    def _make_components(self, options: HeaderInterfaceOptions) -> None:
        with gr.Row():
            with gr.Column(scale=4):
                gr.Markdown(value=f'# {options.title}')
                gr.Markdown(value=f'{options.description}')
            with gr.Column(scale=1):
                dark_mode_button = gr.Button(value='🌙 Dark Mode (深色模式)')

        self._setup(
            dark_mode_button=dark_mode_button,
        )
