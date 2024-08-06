import fastapi
import gradio as gr
import logging
import shirley as sh
import sys
from typing import Tuple


logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


class WebUI(object):

    def __init__(self, client: sh.Client) -> None:
        self._client = client
        self._blocks = self._make_blocks()


    @property
    def client(self) -> sh.Client:
        return self._client

    @property
    def blocks(self) -> gr.Blocks:
        return self._blocks


    def launch(self, *args, **kwargs) -> Tuple[fastapi.FastAPI, str, str]:
        self.blocks.queue(api_open=False)
        return self.blocks.launch(*args, **kwargs)


    def _make_blocks(self, *args, **kwargs) -> gr.Blocks:
        with gr.Blocks(theme=gr.themes.Default(), title='Shirley WebUI') as blocks:
            header = sh.Header()
            header.make_components()

            # with gr.Tab('Chat'):
            #     chat = sh.Chat(client=self.client)
            #     chat.make_components()

            with gr.Tab('Speech'):
                speech = sh.Speech()
                speech.make_components()

            return blocks


def main() -> None:
    # client = sh.Client(pretrained_model_name_or_path=sh.getpath('./models/qwen_vl_chat'))
    client = None
    webui = WebUI(client=client)
    webui.launch(
        share=False,
        inbrowser=False,
        server_port=8000,
        server_name='127.0.0.1',
        favicon_path=sh.getpath('./static/favicon.ico'),
    )


if __name__ == '__main__':
    main()
