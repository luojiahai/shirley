import gradio as gr
import logging
import os
import pypdf
import re
import shirley
import sys
import tempfile
from fastapi import FastAPI
from gradio.events import Dependency
from models.qwen_vl_chat.qwen_generation_utils import HistoryType
from pathlib import Path
from shirley.types import Chatbot, HistoryState, MultimodalTextbox
from shirley.utils import getpath, isimage
from typing import Iterator, List, Tuple


logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


class WebUI(object):

    def __init__(self, client: shirley.Client, tempdir: str) -> None:
        self._client = client
        self._tempdir = tempdir
        self._generating = False
        self._blocks = self._create_gradio_blocks()


    @property
    def client(self) -> shirley.Client:
        return self._client

    @property
    def tempdir(self) -> str:
        return self._tempdir

    @property
    def generating(self) -> bool:
        return self._generating

    @generating.setter
    def generating(self, value) -> None:
        self._generating = value

    @property
    def blocks(self) -> gr.Blocks:
        return self._blocks

    @property
    def dark_mode_button(self) -> gr.Button:
        return self._dark_mode_button

    @property
    def chatbot(self) -> gr.Chatbot:
        return self._chatbot

    @property
    def history(self) -> gr.State:
        return self._history

    @property
    def multimodal_textbox(self) -> gr.MultimodalTextbox:
        return self._multimodal_textbox

    @property
    def submit_button(self) -> gr.Button:
        return self._submit_button

    @property
    def stop_button(self) -> gr.Button:
        return self._stop_button

    @property
    def regenerate_button(self) -> gr.Button:
        return self._regenerate_button

    @property
    def reset_button(self) -> gr.Button:
        return self._reset_button


    @staticmethod
    def parse(text: str) -> str:
        lines = text.split('\n')
        lines = [line for line in lines if line != '']
        count = 0
        for i, line in enumerate(lines):
            if '```' in line:
                count += 1
                items = line.split('`')
                if count % 2 == 1:
                    lines[i] = f'<pre><code class="language-{items[-1]}">'
                else:
                    lines[i] = f'<br></code></pre>'
            else:
                if i > 0:
                    if count % 2 == 1:
                        line = line.replace('`', r'\`')
                        line = line.replace('<', '&lt;')
                        line = line.replace('>', '&gt;')
                        line = line.replace(' ', '&nbsp;')
                        line = line.replace('*', '&ast;')
                        line = line.replace('_', '&lowbar;')
                        line = line.replace('-', '&#45;')
                        line = line.replace('.', '&#46;')
                        line = line.replace('!', '&#33;')
                        line = line.replace('(', '&#40;')
                        line = line.replace(')', '&#41;')
                        line = line.replace('$', '&#36;')
                    lines[i] = '<br>' + line
        return ''.join(lines)


    @staticmethod
    def retrieve(filepath: str) -> str:
        if isimage(filepath):
            return f'Picture: <img>{filepath}</img>'
        elif filepath.endswith('.pdf'):
            reader = pypdf.PdfReader(stream=filepath)
            return '\n'.join([page.extract_text() for page in reader.pages])
        else:
            logger.warning(f'File type {filepath} not supported.')
            return ''


    def generate(self, chatbot: Chatbot, history_state: HistoryState) -> Iterator[Tuple[Chatbot, HistoryState]]:
        self.generating = True
        logger.info(f'🙂 User: {chatbot[-1][0]}')

        history: HistoryType = []
        text = ''
        for _, (query, response) in enumerate(history_state):
            if isinstance(query, (Tuple, List)):
                filepath = query[0]
                context = self.retrieve(filepath=filepath)
                text += context + '\n'
            else:
                text += query
                history.append((text, response))
                text = ''

        query, history = history[-1][0], history[:-1]
        for response in self.client.chat_stream(query=query, history=history):
            if not self.generating: break
            text = self.parse(response)
            text = text.replace('<ref>', '').replace('</ref>', '')
            text = re.sub(r'<box>.*?(</box>|$)', '', text)
            chatbot[-1] = (chatbot[-1][0], text)
            yield chatbot, history_state
            full_response = self.parse(response)

        history.append((query, full_response))
        image_filepath = self.client.draw_bbox_on_latest_picture(history=history, tempdir=self.tempdir)
        if image_filepath: chatbot.append((None, (image_filepath,)))
        else: chatbot[-1] = (chatbot[-1][0], full_response)
        history_state[-1] = (history_state[-1][0], full_response)

        logger.info(f'🦈 Shirley: {full_response}')
        yield chatbot, history_state
        self.generating = False


    def regenerate(self, chatbot: Chatbot, history_state: HistoryState) -> Iterator[Tuple[Chatbot, HistoryState]]:
        if len(chatbot) < 1 or len(history_state) < 1:
            return chatbot, history_state

        state_last = history_state[-1]
        if state_last[1] is None:
            return chatbot, history_state
        history_state[-1] = (state_last[0], None)

        chatbot_last = chatbot.pop(-1)
        if chatbot_last[0] is None:
            chatbot[-1] = (chatbot[-1][0], None)
        else:
            chatbot.append((chatbot_last[0], None))

        yield from self.generate(chatbot=chatbot, history_state=history_state)


    def pregenerate(self) -> Tuple[gr.MultimodalTextbox, gr.Button, gr.Button, gr.Button, gr.Button]:
        components = [
            gr.MultimodalTextbox(interactive=False),
            gr.Button(variant='secondary', interactive=False),
            gr.Button(variant='stop', interactive=True),
            gr.Button(interactive=False),
            gr.Button(interactive=False),
        ]
        return tuple(components)


    def postgenerate(self) -> Tuple[gr.MultimodalTextbox, gr.Button, gr.Button, gr.Button, gr.Button]:
        components = [
            gr.MultimodalTextbox(interactive=True),
            gr.Button(variant='secondary', interactive=False),
            gr.Button(variant='secondary', interactive=False),
            gr.Button(interactive=True),
            gr.Button(interactive=True),
        ]
        return tuple(components)


    def change(self, multimodal_textbox: MultimodalTextbox) -> gr.Button:
        text = multimodal_textbox['text']
        if not text or not text.strip():
            return gr.Button(variant='secondary', interactive=False)
        return gr.Button(variant='primary', interactive=True)


    def submit(
        self, chatbot: Chatbot, history_state: HistoryState, multimodal_textbox: MultimodalTextbox
    ) -> Tuple[Chatbot, HistoryState, MultimodalTextbox]:
        text = multimodal_textbox['text']
        if not text or not text.strip():
            raise gr.Error(visible=False)

        for filepath in multimodal_textbox['files']:
            chatbot = chatbot + [((filepath,), None)]
            history_state = history_state + [((filepath,), None)]

        if multimodal_textbox['text'] is not None:
            chatbot = chatbot + [(self.parse(multimodal_textbox['text']), None)]
            history_state = history_state + [(multimodal_textbox['text'], None)]

        return chatbot, history_state, None


    def stop(self) -> None:
        self.generating = False


    def reset(self) -> Tuple[gr.MultimodalTextbox, gr.Button, gr.Button, gr.Button, gr.Button]:
        components = [
            gr.MultimodalTextbox(interactive=True),
            gr.Button(variant='secondary', interactive=False),
            gr.Button(variant='secondary', interactive=False),
            gr.Button(interactive=False),
            gr.Button(interactive=False),
        ]
        return tuple(components)


    def log(self, chatbot: Chatbot, history_state: HistoryState) -> None:
        logger.info(f'Chatbot: {chatbot}')
        logger.info(f'HistoryState: {history_state}')


    def _create_gradio_blocks(self) -> gr.Blocks:
        with gr.Blocks(theme=gr.themes.Default(), title='Shirley WebUI', fill_width=True) as blocks:
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown(value='# 🦈 Shirley WebUI')
                    gr.Markdown()
                    gr.Markdown(value=
                        'This WebUI is based on [Qwen-VL-Chat](https://modelscope.cn/models/qwen/Qwen-VL-Chat/) \
                        to implement chatbot functionality. \
                        (本WebUI基于[通义千问](https://modelscope.cn/models/qwen/Qwen-VL-Chat/)打造，实现聊天机器人功能。)'
                    )
                    gr.Markdown()
                    gr.Markdown(value=
                        'This WebUI is governed by the original license of Qwen-VL-Chat. We strongly advise users not \
                        to knowingly generate or allow others to knowingly generate harmful content, including hate \
                        speech, violence, pornography, deception, etc. \
                        (本WebUI受通义千问的许可协议限制。我们强烈建议，用户不应传播及不应允许他人传播以下内容，\
                        包括但不限于仇恨言论、暴力、色情、欺诈相关的有害信息。)'
                    )
                    gr.Markdown()
                    self._dark_mode_button = gr.Button(
                        value='🌙 Dark Mode (深色模式)',
                        interactive=True,
                    )

                with gr.Column(scale=3):
                    self._chatbot = gr.Chatbot(
                        label='🦈 Shirley',
                        height='80vh',
                        show_copy_button=True,
                        avatar_images=(None, getpath('./static/apple-touch-icon.png')),
                    )
                    self._history = gr.State(value=[])
                    self._multimodal_textbox = gr.MultimodalTextbox(
                        placeholder='✏️ Enter text or upload file… (输入文字或者上传文件…)',
                        show_label=False,
                        interactive=True,
                    )

                    with gr.Row():
                        self._submit_button = gr.Button(
                            value='🚀 Submit (发送)',
                            variant='secondary',
                            interactive=False,
                        )
                        self._stop_button = gr.Button(
                            value='⏹️ Stop (停止生成)',
                            variant='secondary',
                            interactive=False,
                        )
                        self._regenerate_button = gr.Button(
                            value='🤔️ Regenerate (重新生成)',
                            interactive=False,
                        )
                        self._reset_button = gr.Button(
                            value='🧹 Reset (重置对话)',
                            interactive=False,
                        )

            self.__subscribe_events()
            return blocks


    def __subscribe_events(self) -> None:
        self.dark_mode_button.click(
            fn=None,
            js='() => { document.body.classList.toggle("dark"); }',
            show_api=False,
        )

        self.multimodal_textbox.change(
            fn=self.change,
            inputs=[self.multimodal_textbox],
            outputs=[self.submit_button],
            show_api=False,
        )

        multimodal_textbox_submit = self.multimodal_textbox.submit(
            fn=self.submit,
            inputs=[self.chatbot, self.history, self.multimodal_textbox],
            outputs=[self.chatbot, self.history, self.multimodal_textbox],
            show_api=False,
        )
        self.__subscribe_events_generate(dependency=multimodal_textbox_submit, generate_fn=self.generate)

        submit_button_click = self.submit_button.click(
            fn=self.submit,
            inputs=[self.chatbot, self.history, self.multimodal_textbox],
            outputs=[self.chatbot, self.history, self.multimodal_textbox],
            show_api=False,
        )
        self.__subscribe_events_generate(dependency=submit_button_click, generate_fn=self.generate)

        self.stop_button.click(fn=self.stop, show_api=False)

        regenerate_button_click = self.regenerate_button.click(fn=lambda:None, show_api=False)
        self.__subscribe_events_generate(dependency=regenerate_button_click, generate_fn=self.regenerate)

        self.reset_button.click(
            fn=lambda: ([], [], None),
            inputs=[],
            outputs=[self.chatbot, self.history, self.multimodal_textbox],
            show_api=False,
        ).then(
            fn=self.reset,
            inputs=[],
            outputs=[
                self.multimodal_textbox,
                self.submit_button,
                self.stop_button,
                self.regenerate_button,
                self.reset_button,
            ],
            show_api=False,
        )


    def __subscribe_events_generate(self, dependency: Dependency, generate_fn):
        dependency.success(
            fn=self.pregenerate,
            inputs=[],
            outputs=[
                self.multimodal_textbox,
                self.submit_button,
                self.stop_button,
                self.regenerate_button,
                self.reset_button,
            ],
            show_api=False,
        ).then(
            fn=generate_fn,
            inputs=[self.chatbot, self.history],
            outputs=[self.chatbot, self.history],
            show_progress=True,
            show_api=False,
        ).then(
            fn=self.postgenerate,
            inputs=[],
            outputs=[
                self.multimodal_textbox,
                self.submit_button,
                self.stop_button,
                self.regenerate_button,
                self.reset_button,
            ],
            show_api=False,
        ).then(
            fn=self.log,
            inputs=[self.chatbot, self.history],
            outputs=[],
            show_api=False,
        )


    def launch(self) -> Tuple[FastAPI, str, str]:
        self.blocks.queue()
        return self.blocks.launch(
            share=False,
            inbrowser=False,
            server_port=8000,
            server_name='127.0.0.1',
            favicon_path=getpath('./static/favicon.ico'),
        )


def main() -> None:
    client = shirley.Client(pretrained_model_path=getpath('./models/qwen_vl_chat'))
    tempdir = os.environ.get('GRADIO_TEMP_DIR') or str(Path(tempfile.gettempdir()) / 'gradio')
    webui = WebUI(client, tempdir)
    webui.launch()


if __name__ == '__main__':
    main()
