import gradio as gr
import logging
import sys
from .interface import Interface


logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


class Header(Interface):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__()

        self._make_components(*args, **kwargs)


    def _setup_dark_mode_button(self, *args, **kwargs) -> None:
        dark_mode_button: gr.Button = kwargs['dark_mode_button']

        dark_mode_button.click(
            fn=None,
            js='() => { document.body.classList.toggle(\'dark\'); }',
            show_api=False,
        )


    def _setup(self, *args, **kwargs) -> None:
        self._setup_dark_mode_button(*args, **kwargs)


    def _make_components(self, *args, **kwargs) -> None:
        with gr.Row():
            with gr.Column(scale=4):
                gr.Markdown(value='# 🦈 Shirley WebUI')
                gr.Markdown(
                    value='It is just doing some stuff intelligently. This WebUI is built by \
                    [luojiahai](https://luojiahai.com).'
                )
            with gr.Column(scale=1):
                dark_mode_button = gr.Button(value='🌙 Dark Mode (深色模式)')

        self._setup(
            dark_mode_button=dark_mode_button,
        )
