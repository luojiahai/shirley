import gradio as gr
import logging
import shirley as sh
import sys


logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


class Header(sh.Component):
    
    def __init__(self) -> None:
        pass


    def _setup_dark_mode_button(self, *args, **kwargs) -> None:
        dark_mode_button: gr.Button = kwargs['dark_mode_button']

        dark_mode_button.click(
            fn=None,
            js='() => { document.body.classList.toggle(\'dark\'); }',
            show_api=False,
        )

    
    def _setup(self, *args, **kwargs) -> None:
        self._setup_dark_mode_button(*args, **kwargs)


    def make_components(self, *args, **kwargs) -> None:
        with gr.Row():
            with gr.Column(scale=10):
                gr.Markdown(value='# 🦈 Shirley WebUI')
            with gr.Column(scale=3):
                dark_mode_button = gr.Button(value='🌙 Dark Mode (深色模式)')
        
        self._setup(
            dark_mode_button=dark_mode_button,
        )
