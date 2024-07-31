import gradio as gr
import logging
import pypdf
import re
import shirley
import sys
import tempfile
from fastapi import FastAPI
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


    def augment(self, history_state: HistoryState) -> Tuple[str, HistoryType]:
        history = []
        text = ''
        for _, (raw_query, response) in enumerate(history_state):
            if isinstance(raw_query, (Tuple, List)):
                filepath = raw_query[0]
                context = self.retrieve(filepath=filepath)
                text += context + '\n'
            else:
                text += raw_query
                history.append((text, response))
                text = ''
        return history[-1][0], history[:-1]


    def generate(self, chatbot: Chatbot, history_state: HistoryState) -> Iterator[Tuple[Chatbot, HistoryState]]:
        logger.debug('Generate')

        self._generating = True
        logger.info(f'🙂 User: {chatbot[-1][0]}')

        query, history = self.augment(history_state)
        for response in self.client.chat_stream(query=query, history=history):
            if not self._generating: break
            text = self.parse(response)
            text = text.replace('<ref>', '').replace('</ref>', '')
            text = re.sub(r'<box>.*?(</box>|$)', '', text)
            chatbot[-1] = (chatbot[-1][0], text)
            yield chatbot, history_state
            full_response = self.parse(response)

        history.append((query, full_response))
        image_filepath = self.client.draw_bbox_on_latest_picture(history=history, tempdir=self._tempdir)
        if image_filepath: chatbot.append((None, (image_filepath,)))
        else: chatbot[-1] = (chatbot[-1][0], full_response)
        history_state[-1] = (history_state[-1][0], full_response)

        logger.info(f'🦈 Shirley: {full_response}')
        yield chatbot, history_state
        self._generating = False


    def regenerate(self, chatbot: Chatbot, history_state: HistoryState) -> Tuple[Chatbot, HistoryState]:
        logger.debug('Regenerate')

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

        return chatbot, history_state


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


    def validate(self, multimodal_textbox: MultimodalTextbox) -> None:
        text = multimodal_textbox['text']
        if not text or not text.strip():
            raise gr.Error(visible=False)
        return


    def submit(
        self,
        chatbot: Chatbot,
        history_state: HistoryState,
        multimodal_textbox: MultimodalTextbox,
    ) -> Tuple[Chatbot, HistoryState, MultimodalTextbox]:
        logger.debug('Submit')

        for filepath in multimodal_textbox['files']:
            chatbot = chatbot + [((filepath,), None)]
            history_state = history_state + [((filepath,), None)]

        if multimodal_textbox['text'] is not None:
            chatbot = chatbot + [(self.parse(multimodal_textbox['text']), None)]
            history_state = history_state + [(multimodal_textbox['text'], None)]

        return chatbot, history_state, None


    def stop(self) -> None:
        logger.debug('Stop')
        self._generating = False


    def reset(self) -> Tuple[Chatbot, HistoryState, MultimodalTextbox]:
        logger.debug('Reset')
        return [], [], None


    def postreset(self) -> Tuple[gr.MultimodalTextbox, gr.Button, gr.Button, gr.Button, gr.Button]:
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


    def blocks(self) -> gr.Blocks:
        with gr.Blocks(
            theme=gr.themes.Default(),
            title='Shirley WebUI',
            fill_width=True,
        ) as blocks:
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown(value='# 🦈 Shirley WebUI')
                    gr.Markdown()
                    gr.Markdown(value='### 🪺 Source (源代码)')
                    gr.Markdown(value='https://github.com/luojiahai/shirley')
                    gr.Markdown()
                    gr.Markdown(value='### 🏷️ Description (描述)')
                    gr.Markdown(value=
                        'This WebUI is based on [Qwen-VL-Chat](https://modelscope.cn/models/qwen/Qwen-VL-Chat/) \
                        to implement chatbot functionality. \
                        (本WebUI基于[通义千问](https://modelscope.cn/models/qwen/Qwen-VL-Chat/)打造，实现聊天机器人功能。)'
                    )
                    gr.Markdown()
                    gr.Markdown(value='### ⚠️ Note (注意事项)')
                    gr.Markdown(value=
                        'This WebUI is governed by the original license of Qwen-VL-Chat. We strongly advise users not \
                        to knowingly generate or allow others to knowingly generate harmful content, including hate \
                        speech, violence, pornography, deception, etc. \
                        (本WebUI受通义千问的许可协议限制。我们强烈建议，用户不应传播及不应允许他人传播以下内容，\
                        包括但不限于仇恨言论、暴力、色情、欺诈相关的有害信息。)'
                    )
                    gr.Markdown()
                    toggle_dark = gr.Button(value='🔦 Toggle Light/Dark Mode (切换浅色/深色模式)')

                with gr.Column(scale=3):
                    chatbot = gr.Chatbot(
                        label='🦈 Shirley',
                        height='80vh',
                        show_copy_button=True,
                        avatar_images=(None, getpath('./static/apple-touch-icon.png')),
                    )
                    history_state = gr.State(value=[])
                    multimodal_textbox = gr.MultimodalTextbox(
                        placeholder='✏️ Enter text or upload file… (输入文字或者上传文件…)',
                        show_label=False,
                        interactive=True,
                        submit_btn=False,
                    )

                    with gr.Row():
                        submit_button = gr.Button(value='🚀 Submit (发送)', variant='secondary', interactive=False)
                        stop_button = gr.Button(value='⏹️ Stop (停止生成)', variant='secondary', interactive=False)
                        regenerate_button = gr.Button(value='🤔️ Regenerate (重新生成)', interactive=False)
                        reset_button = gr.Button(value='🧹 Reset (重置对话)', interactive=False)

            toggle_dark \
                .click(
                    fn=None,
                    js='() => { document.body.classList.toggle("dark"); }',
                    show_api=False,
                )

            multimodal_textbox \
                .change(
                    fn=self.change,
                    inputs=[multimodal_textbox],
                    outputs=[submit_button],
                    show_api=False,
                )

            multimodal_textbox \
                .submit(
                    fn=self.validate,
                    inputs=[multimodal_textbox],
                    outputs=[],
                    show_api=False,
                ) \
                .success(
                    fn=self.submit,
                    inputs=[chatbot, history_state, multimodal_textbox],
                    outputs=[chatbot, history_state, multimodal_textbox],
                ) \
                .then(
                    fn=self.pregenerate,
                    inputs=[],
                    outputs=[multimodal_textbox, submit_button, stop_button, regenerate_button, reset_button],
                    show_api=False,
                ) \
                .then(
                    fn=self.generate,
                    inputs=[chatbot, history_state],
                    outputs=[chatbot, history_state],
                    show_progress=True,
                ) \
                .then(
                    fn=self.postgenerate,
                    inputs=[],
                    outputs=[multimodal_textbox, submit_button, stop_button, regenerate_button, reset_button],
                    show_api=False,
                ) \
                .then(
                    fn=self.log,
                    inputs=[chatbot, history_state],
                    outputs=[],
                    show_api=False,
                )

            submit_button \
                .click(
                    fn=self.validate,
                    inputs=[multimodal_textbox],
                    outputs=[],
                    show_api=False,
                ) \
                .success(
                    fn=self.submit,
                    inputs=[chatbot, history_state, multimodal_textbox],
                    outputs=[chatbot, history_state, multimodal_textbox],
                    show_api=False,
                ) \
                .then(
                    fn=self.pregenerate,
                    inputs=[],
                    outputs=[multimodal_textbox, submit_button, stop_button, regenerate_button, reset_button],
                    show_api=False,
                ) \
                .then(
                    fn=self.generate,
                    inputs=[chatbot, history_state],
                    outputs=[chatbot, history_state],
                    show_progress=True,
                    show_api=False,
                ) \
                .then(
                    fn=self.postgenerate,
                    inputs=[],
                    outputs=[multimodal_textbox, submit_button, stop_button, regenerate_button, reset_button],
                    show_api=False,
                ) \
                .then(
                    fn=self.log,
                    inputs=[chatbot, history_state],
                    outputs=[],
                    show_api=False,
                )

            stop_button.click(fn=self.stop)

            regenerate_button \
                .click(
                    fn=self.regenerate,
                    inputs=[chatbot, history_state],
                    outputs=[chatbot, history_state],
                    show_progress=True,
                ) \
                .then(
                    fn=self.pregenerate,
                    inputs=[],
                    outputs=[multimodal_textbox, submit_button, stop_button, regenerate_button, reset_button],
                    show_api=False,
                ) \
                .then(
                    fn=self.generate,
                    inputs=[chatbot, history_state],
                    outputs=[chatbot, history_state],
                    show_progress=True,
                    show_api=False,
                ) \
                .then(
                    fn=self.postgenerate,
                    inputs=[],
                    outputs=[multimodal_textbox, submit_button, stop_button, regenerate_button, reset_button],
                    show_api=False,
                ) \
                .then(
                    fn=self.log,
                    inputs=[chatbot, history_state],
                    outputs=[],
                    show_api=False,
                )

            reset_button \
                .click(
                    fn=self.reset,
                    inputs=[],
                    outputs=[chatbot, history_state, multimodal_textbox],
                    show_progress=True,
                    api_name='reset',
                ) \
                .then(
                    fn=self.postreset,
                    inputs=[],
                    outputs=[multimodal_textbox, submit_button, stop_button, regenerate_button, reset_button],
                    show_api=False,
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
    client = shirley.Client(pretrained_model_path=getpath('./models/qwen_vl_chat'))
    tempdir = str(Path(tempfile.gettempdir()) / 'gradio')
    webui = WebUI(client, tempdir)
    webui.launch()


if __name__ == '__main__':
    main()
