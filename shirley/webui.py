import fastapi
import gradio as gr
import logging
import shirley as sh
import sys
from typing import Tuple


logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


class WebUI(object):

    def __init__(self) -> None:
        self._blocks = self._make_blocks()


    @property
    def blocks(self) -> gr.Blocks:
        return self._blocks


    def launch(self, *args, **kwargs) -> Tuple[fastapi.FastAPI, str, str]:
        self.blocks.queue()
        return self.blocks.launch(*args, **kwargs)


    def _make_blocks(self, *args, **kwargs) -> gr.Blocks:
        header = sh.interfaces.Header()
        chat = sh.interfaces.Chat()
        tts = sh.interfaces.TextToSpeech()
        footer = sh.interfaces.Footer()

        avatar_images=(
            sh.utils.getpath('./static/images/grinning-face.png'),
            sh.utils.getpath('./static/images/shark.png'),
        )

        with gr.Blocks(
            theme=gr.themes.Default(
                primary_hue=gr.themes.colors.cyan,
                secondary_hue=gr.themes.colors.sky,
                radius_size=gr.themes.sizes.radius_none,
            ),
            title='Shirley WebUI',
            css=sh.utils.getpath('./static/css/custom.css'),
        ) as blocks:
            header.make_components()
            with gr.Tab('✨ Chat (聊天/唠嗑)'):
                chat.make_components(avatar_images=avatar_images)
            with gr.Tab('💬 Text-To-Speech (文字转语音)'):
                tts.make_components()
            footer.make_components()
            return blocks


def main() -> None:
    webui = WebUI()
    webui.launch(
        server_name='127.0.0.1',
        server_port=8000,
        favicon_path=sh.utils.getpath('./static/favicon.ico'),
        show_api=False,
    )


if __name__ == '__main__':
    main()
