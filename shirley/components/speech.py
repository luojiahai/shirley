
import gradio as gr
import logging
import shirley as sh
import sys


logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


class Speech(sh.Component):

    def __init__(self) -> None:
        pass


    def _setup(self, *args, **kwargs) -> None:
        pass


    def make_components(self, *args, **kwargs) -> None:
        with gr.Row():
            with gr.Column():
                textbox = gr.Textbox(lines=10)
                convert_button = gr.Button(value='↪️ Convert (转换)', variant='primary')
            with gr.Column():
                audio = gr.Audio(interactive=False)

        self._setup()
