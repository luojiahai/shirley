import gradio
import logging
import pypdf
import re
import shirley
import sys
import tempfile
from fastapi import FastAPI
from gradio.components.multimodal_textbox import MultimodalValue
from models.qwen_vl_chat.qwen_generation_utils import HistoryType
from pathlib import Path
from shirley.types import Chatbot, HistoryState
from shirley.utils import getpath, isimage
from typing import Iterator, List, Tuple


logger = logging.getLogger(__name__)


class WebUI(object):

    def __init__(self, client: shirley.Client, tempdir: str) -> None:
        self._client = client
        self._tempdir = tempdir
        self._generating = False


    @property
    def client(self) -> shirley.Client:
        return self._client


    def parse(self, text: str) -> str:
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


    def retrieve(self, filepath: str) -> str:
        if isimage(filepath):
            return f'Picture: <img>{filepath}</img>'
        elif filepath.endswith('.pdf'):
            reader = pypdf.PdfReader(stream=filepath)
            return '\n'.join([page.extract_text() for page in reader.pages])
        else:
            logger.warning(f'File type {filepath} not supported.')
            return ''


    def augment(self, state: HistoryState) -> Tuple[str, HistoryType]:
        history = []
        text = ''
        for _, (raw_query, response) in enumerate(state):
            if isinstance(raw_query, (Tuple, List)):
                filepath = raw_query[0]
                context = self.retrieve(filepath=filepath)
                text += context + '\n'
            else:
                text += raw_query
                history.append((text, response))
                text = ''
        return history[-1][0], history[:-1]


    def generate(self, chatbot: Chatbot, state: HistoryState) -> Iterator[Tuple[Chatbot, HistoryState]]:
        self._generating = True
        logger.debug('generate')
        logger.info(f'🙂 User: {chatbot[-1][0]}')

        query, history = self.augment(state)
        for response in self.client.chat_stream(query=query, history=history):
            if not self._generating: break
            text = self.parse(response)
            text = text.replace('<ref>', '').replace('</ref>', '')
            text = re.sub(r'<box>.*?(</box>|$)', '', text)
            chatbot[-1] = (chatbot[-1][0], text)
            yield chatbot, state
            full_response = self.parse(response)

        history.append((query, full_response))
        image_filepath = self.client.draw_bbox_on_latest_picture(history=history, tempdir=self._tempdir)
        if image_filepath: chatbot.append((None, (image_filepath,)))
        else: chatbot[-1] = (chatbot[-1][0], full_response)
        state[-1] = (state[-1][0], full_response)

        logger.info(f'🦈 Shirley: {full_response}')
        yield chatbot, state
        self._generating = False


    def regenerate(self, chatbot: Chatbot, state: HistoryState) -> Tuple[Chatbot, HistoryState]:
        logger.debug('regenerate')

        if len(chatbot) < 1 or len(state) < 1:
            return chatbot, state

        state_last = state[-1]
        if state_last[1] is None:
            return chatbot, state
        state[-1] = (state_last[0], None)

        chatbot_last = chatbot.pop(-1)
        if chatbot_last[0] is None:
            chatbot[-1] = (chatbot[-1][0], None)
        else:
            chatbot.append((chatbot_last[0], None))

        return chatbot, state


    def submit(
        self,
        chatbot: Chatbot,
        state: HistoryState,
        textbox: MultimodalValue
    ) -> Tuple[Chatbot, HistoryState, MultimodalValue]:
        logger.debug('submit')
        for filepath in textbox["files"]:
            chatbot = chatbot + [((filepath,), None)]
            state = state + [((filepath,), None)]
        if textbox["text"] is not None:
            chatbot = chatbot + [(self.parse(textbox["text"]), None)]
            state = state + [(textbox["text"], None)]
        return chatbot, state, gradio.MultimodalTextbox(value=None, interactive=False)


    def pre_generate(self): # outputs=[stop_button, regenerate_button]
        components = [
            gradio.Button(interactive=True),
            gradio.Button(interactive=False),
        ]
        return tuple(components)


    def post_generate(self): # outputs=[textbox, stop_button, regenerate_button]
        components = [
            gradio.MultimodalTextbox(interactive=True),
            gradio.Button(interactive=False),
            gradio.Button(interactive=True)
        ]
        return tuple(components)


    def stop(self):
        self._generating = False


    def log(self, chatbot: Chatbot, state: HistoryState) -> None:
        logger.debug('log')
        logger.info(f'chatbot: {chatbot}')
        logger.info(f'state: {state}')


    def blocks(self) -> gradio.Blocks:
        with gradio.Blocks(title='Shirley WebUI', css=getpath('./shirley/css/custom.css')) as blocks:

            with gradio.Row():
                with gradio.Column(scale=10):
                    gradio.Markdown('# 🦈 Shirley WebUI')
                    gradio.Markdown(
                        'This WebUI is based on [Qwen-VL-Chat](https://modelscope.cn/models/qwen/Qwen-VL-Chat/) \
                        to implement chatbot functionality. \
                        (本WebUI基于[通义千问](https://modelscope.cn/models/qwen/Qwen-VL-Chat/)打造，实现聊天机器人功能。)'
                    )

                with gradio.Column(scale=2):
                    toggle_dark = gradio.Button(value='🔦 Toggle Dark (切换暗黑模式)')

            chatbot = gradio.Chatbot(
                label='🦈 Shirley',
                height='70vh',
                show_copy_button=True,
                avatar_images=(None, getpath('./static/apple-touch-icon.png'))
            )

            state = gradio.State(value=[])

            textbox = gradio.MultimodalTextbox(
                placeholder='✏️ Enter text or upload file… (输入文字或者上传文件…)',
                show_label=False,
                interactive=True,
            )

            with gradio.Row():
                stop_button = gradio.Button('⏹️ Stop (停止生成)', interactive=False)
                regenerate_button = gradio.Button('🤔️ Regenerate (重新生成)', interactive=False)
                clear_button = gradio.Button('🧹 Clear (清除历史)')

            toggle_dark \
                .click(
                    fn=None,
                    js='() => { document.body.classList.toggle("dark"); }',
                )

            textbox \
                .submit(
                    fn=self.submit,
                    inputs=[chatbot, state, textbox],
                    outputs=[chatbot, state, textbox],
                ) \
                .then(
                    fn=self.pre_generate,
                    inputs=[],
                    outputs=[stop_button, regenerate_button],
                ) \
                .then(
                    fn=self.generate,
                    inputs=[chatbot, state],
                    outputs=[chatbot, state],
                    show_progress=True,
                ) \
                .then(
                    fn=self.post_generate,
                    inputs=[],
                    outputs=[textbox, stop_button, regenerate_button],
                ) \
                .then(
                    fn=self.log,
                    inputs=[chatbot, state],
                    outputs=[],
                    show_api=False,
                )

            stop_button \
                .click(fn=self.stop)

            regenerate_button \
                .click(
                    fn=self.regenerate,
                    inputs=[chatbot, state],
                    outputs=[chatbot, state],
                    show_progress=True,
                ) \
                .then(
                    fn=self.pre_generate,
                    inputs=[],
                    outputs=[stop_button, regenerate_button],
                ) \
                .then(
                    fn=self.generate,
                    inputs=[chatbot, state],
                    outputs=[chatbot, state],
                    show_progress=True,
                    show_api=False,
                ) \
                .then(
                    fn=self.post_generate,
                    inputs=[],
                    outputs=[textbox, stop_button, regenerate_button],
                ) \
                .then(
                    fn=self.log,
                    inputs=[chatbot, state],
                    outputs=[],
                    show_api=False,
                )

            clear_button \
                .click(
                    fn=lambda: ([], []),
                    inputs=[],
                    outputs=[chatbot, state],
                    show_progress=True,
                    api_name='clear',
                )

            gradio.Markdown(
                '<font size=2>Note: This WebUI is governed by the original license of Qwen-VL-Chat. We strongly advise \
                users not to knowingly generate or allow others to knowingly generate harmful content, including hate \
                speech, violence, pornography, deception, etc. \
                (注：本WebUI受通义千问的许可协议限制。我们强烈建议，用户不应传播及不应允许他人传播以下内容，\
                包括但不限于仇恨言论、暴力、色情、欺诈相关的有害信息。)'
            )

            return blocks


    def launch(self) -> Tuple[FastAPI, str, str]:
        blocks = self.blocks()
        return blocks.queue().launch(
            share=False,
            inbrowser=False,
            server_port=8000,
            server_name='127.0.0.1',
            favicon_path=getpath('./static/favicon.ico'),
        )


def main() -> None:
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    client = shirley.Client(pretrained_model_path=getpath('./models/qwen_vl_chat'))
    tempdir = str(Path(tempfile.gettempdir()) / 'gradio')
    webui = WebUI(client, tempdir)
    webui.launch()


if __name__ == '__main__':
    main()
