import fastapi
import gradio as gr
import logging
import os
import pathlib
import pypdf
import re
import shirley as sh
import sys
import tempfile
from gradio.events import Dependency
from typing import Callable, List, Tuple


logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


class WebUI(object):

    tempdir = os.environ.get('GRADIO_TEMP_DIR') or str(pathlib.Path(tempfile.gettempdir()) / 'gradio')


    def __init__(self, client: sh.Client) -> None:
        self._client = client
        self._generating = False
        self._blocks = self._initialise_interface()


    @property
    def client(self) -> sh.Client:
        return self._client

    @property
    def generating(self) -> bool:
        return self._generating

    @generating.setter
    def generating(self, value) -> None:
        self._generating = value

    @property
    def blocks(self) -> gr.Blocks:
        return self._blocks


    def launch(self, *args, **kwargs) -> Tuple[fastapi.FastAPI, str, str]:
        self.blocks.queue(api_open=False)
        return self.blocks.launch(*args, **kwargs)


    @staticmethod
    def _parse(text: str, remove_image_tags: bool = False) -> str:
        lines = text.split('\n')
        lines = [line for line in lines if line != '']
        count = 0
        for i, line in enumerate(lines):
            if '```' in line:
                count += 1
                items = line.split('`')
                if count % 2 == 1:
                    lines[i] = f'<pre><code class=\'language-{items[-1]}\'>'
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

        text = ''.join(lines)
        if remove_image_tags:
            text = text.replace('<ref>', '').replace('</ref>', '')
            text = re.sub(r'<box>.*?(</box>|$)', '', text)
        return text


    @staticmethod
    def _load_context(filepath: str) -> str:
        if sh.isimage(filepath):
            return f'Picture: <img>{filepath}</img>'
        elif filepath.endswith('.pdf'):
            reader = pypdf.PdfReader(stream=filepath)
            return '\n'.join([page.extract_text() for page in reader.pages])
        else:
            logger.warning(f'File type {filepath} not supported.')
            return ''


    def _get_query_and_chat_history(self, history: sh.HistoryInput) -> Tuple[str, sh.ChatHistory]:
        chat_history: sh.ChatHistory = []
        text = ''
        for _, (query, response) in enumerate(history):
            if isinstance(query, (Tuple, List)):
                filepath = query[0]
                context = self._load_context(filepath=filepath)
                text += context + '\n'
            else:
                text += query
                chat_history.append((text, response))
                text = ''
        return chat_history[-1][0], chat_history[:-1]


    def _generate(self, *args, **kwargs) -> sh.BlocksOutput:
        chatbot: sh.ChatbotTuplesInput = args[0]
        history: sh.HistoryInput = args[1]

        self.generating = True
        logger.info(f'🙂 User: {chatbot[-1][0]}')

        query, chat_history = self._get_query_and_chat_history(history)
        full_response = ''
        for response in self.client.chat_stream(query=query, history=chat_history):
            if not self.generating: break
            chatbot[-1] = (chatbot[-1][0], self._parse(text=response, remove_image_tags=True))
            yield chatbot, history
            full_response = self._parse(text=response)

        chat_history.append((query, full_response))
        image_filepath = self.client.draw_bbox_on_latest_picture(history=chat_history, tempdir=self.tempdir)
        if image_filepath is not None:
            chatbot.append((None, (image_filepath,)))
        else:
            chatbot[-1] = (chatbot[-1][0], full_response)
        history[-1] = (history[-1][0], full_response)

        logger.info(f'🦈 Shirley: {full_response}')
        self.generating = False
        yield chatbot, history


    def _regenerate(self, *args, **kwargs) -> sh.BlocksOutput:
        chatbot: sh.ChatbotTuplesInput = args[0]
        history: sh.HistoryInput = args[1]

        if len(chatbot) < 1 or len(history) < 1:
            return chatbot, history

        state_last = history[-1]
        if state_last[1] is None:
            return chatbot, history
        history[-1] = (state_last[0], None)

        chatbot_last = chatbot.pop(-1)
        if chatbot_last[0] is None:
            chatbot[-1] = (chatbot[-1][0], None)
        else:
            chatbot.append((chatbot_last[0], None))

        yield from self._generate(*args, **kwargs)


    def _submit(self, *args, **kwargs) -> sh.BlocksOutput:
        chatbot: sh.ChatbotTuplesInput = args[0]
        history: sh.HistoryInput = args[1]
        multimodal_textbox: sh.MultimodalTextboxInput = args[2]

        text = multimodal_textbox['text']
        if not text or not text.strip():
            raise gr.Error(visible=False)

        for filepath in multimodal_textbox['files']:
            chatbot = chatbot + [((filepath,), None)]
            history = history + [((filepath,), None)]

        if multimodal_textbox['text'] is not None:
            chatbot = chatbot + [(self._parse(text=multimodal_textbox['text']), None)]
            history = history + [(multimodal_textbox['text'], None)]

        return chatbot, history, None


    def _change(self, *args, **kwargs) -> sh.ComponentsOutput:
        multimodal_textbox: sh.MultimodalTextboxInput = args[0]

        text = multimodal_textbox['text']
        if not text or not text.strip():
            return gr.Button(variant='secondary', interactive=False)

        return gr.Button(variant='primary', interactive=True)


    def _pregenerate(self, *args, **kwargs) -> sh.ComponentsOutput:
        components = [
            gr.MultimodalTextbox(interactive=False),
            gr.Button(variant='secondary', interactive=False),
            gr.Button(variant='stop', interactive=True),
            gr.Button(interactive=False),
            gr.Button(interactive=False),
        ]
        return tuple(components)


    def _postgenerate(self, *args, **kwargs) -> sh.ComponentsOutput:
        components = [
            gr.MultimodalTextbox(interactive=True),
            gr.Button(variant='secondary', interactive=False),
            gr.Button(variant='secondary', interactive=False),
            gr.Button(interactive=True),
            gr.Button(interactive=True),
        ]
        return tuple(components)


    def _stop(self, *args, **kwargs) -> sh.ComponentsOutput:
        self.generating = False


    def _reset(self, *args, **kwargs) -> sh.ComponentsOutput:
        components = [
            gr.MultimodalTextbox(interactive=True),
            gr.Button(variant='secondary', interactive=False),
            gr.Button(variant='secondary', interactive=False),
            gr.Button(interactive=False),
            gr.Button(interactive=False),
        ]
        return tuple(components)


    def _log(self, *args, **kwargs) -> sh.ComponentsOutput:
        chatbot: sh.ChatbotTuplesInput = args[0]
        history: sh.HistoryInput = args[1]

        logger.info(f'Chatbot: {chatbot}')
        logger.info(f'History: {history}')


    def _set_event_trigger_generate(self, dependency: Dependency, fn: Callable, *args, **kwargs) -> None:
        chatbot: gr.Chatbot = kwargs['chatbot']
        history: gr.State = kwargs['history']
        multimodal_textbox: gr.MultimodalTextbox = kwargs['multimodal_textbox']
        submit_button: gr.Button = kwargs['submit_button']
        stop_button: gr.Button = kwargs['stop_button']
        regenerate_button: gr.Button = kwargs['regenerate_button']
        reset_button: gr.Button = kwargs['reset_button']

        success = dependency.success(fn=lambda:None, show_api=False)
        pregenerate = success.then(
            fn=self._pregenerate,
            inputs=None,
            outputs=[multimodal_textbox, submit_button, stop_button, regenerate_button, reset_button],
            show_api=False,
        )
        generate = pregenerate.then(
            fn=fn,
            inputs=[chatbot, history],
            outputs=[chatbot, history],
            show_progress=True,
            show_api=False,
        )
        postgenerate = generate.then(
            fn=self._postgenerate,
            inputs=None,
            outputs=[multimodal_textbox, submit_button, stop_button, regenerate_button, reset_button],
            show_api=False,
        )
        postgenerate.then(
            fn=self._log,
            inputs=[chatbot, history],
            outputs=None,
            show_api=False,
        )


    def _configure_dark_mode_button(self, *args, **kwargs) -> None:
        dark_mode_button: gr.Button = kwargs['dark_mode_button']

        dark_mode_button.click(
            fn=None,
            js='() => { document.body.classList.toggle(\'dark\'); }',
            show_api=False,
        )


    def _configure_multimodal_textbox(self, *args, **kwargs) -> None:
        chatbot: gr.Chatbot = kwargs['chatbot']
        history: gr.State = kwargs['history']
        multimodal_textbox: gr.MultimodalTextbox = kwargs['multimodal_textbox']
        submit_button: gr.Button = kwargs['submit_button']

        multimodal_textbox.change(
            fn=self._change,
            inputs=[multimodal_textbox],
            outputs=[submit_button],
            show_api=False,
        )

        submit = multimodal_textbox.submit(
            fn=self._submit,
            inputs=[chatbot, history, multimodal_textbox],
            outputs=[chatbot, history, multimodal_textbox],
            show_api=False,
        )
        self._set_event_trigger_generate(dependency=submit, fn=self._generate, *args, **kwargs)


    def _configure_submit_button(self, *args, **kwargs) -> None:
        chatbot: gr.Chatbot = kwargs['chatbot']
        history: gr.State = kwargs['history']
        multimodal_textbox: gr.MultimodalTextbox = kwargs['multimodal_textbox']
        submit_button: gr.Button = kwargs['submit_button']

        click = submit_button.click(
            fn=self._submit,
            inputs=[chatbot, history, multimodal_textbox],
            outputs=[chatbot, history, multimodal_textbox],
            show_api=False,
        )
        self._set_event_trigger_generate(dependency=click, fn=self._generate, *args, **kwargs)


    def _configure_stop_button(self, *args, **kwargs) -> None:
        stop_button: gr.Button = kwargs['stop_button']

        stop_button.click(fn=self._stop, show_api=False)


    def _configure_regenerate_button(self, *args, **kwargs) -> None:
        regenerate_button: gr.Button = kwargs['regenerate_button']

        click = regenerate_button.click(fn=lambda:None, show_api=False)
        self._set_event_trigger_generate(dependency=click, fn=self._regenerate, *args, **kwargs)


    def _configure_reset_button(self, *args, **kwargs) -> None:
        chatbot: gr.Chatbot = kwargs['chatbot']
        history: gr.State = kwargs['history']
        multimodal_textbox: gr.MultimodalTextbox = kwargs['multimodal_textbox']
        submit_button: gr.Button = kwargs['submit_button']
        stop_button: gr.Button = kwargs['stop_button']
        regenerate_button: gr.Button = kwargs['regenerate_button']
        reset_button: gr.Button = kwargs['reset_button']

        reset_button_click = reset_button.click(
            fn=lambda: ([], [], None),
            inputs=None,
            outputs=[chatbot, history, multimodal_textbox],
            show_api=False,
        )
        reset_button_click.then(
            fn=self._reset,
            inputs=None,
            outputs=[multimodal_textbox, submit_button, stop_button, regenerate_button, reset_button],
            show_api=False,
        )


    def _configure_components(self, *args, **kwargs) -> None:
        self._configure_dark_mode_button(*args, **kwargs)
        self._configure_multimodal_textbox(*args, **kwargs)
        self._configure_submit_button(*args, **kwargs)
        self._configure_stop_button(*args, **kwargs)
        self._configure_regenerate_button(*args, **kwargs)
        self._configure_reset_button(*args, **kwargs)


    def _initialise_interface(self, *args, **kwargs) -> gr.Blocks:
        with (
            gr.Blocks(theme=gr.themes.Default(), title='Shirley WebUI', fill_width=True) as blocks,
            gr.Row(),
        ):
            with gr.Column(scale=1):
                gr.Markdown(value='# 🦈 Shirley WebUI')
                gr.Markdown()
                gr.Markdown(
                    value='This WebUI is based on [Qwen-VL-Chat](https://modelscope.cn/models/qwen/Qwen-VL-Chat/) \
                    to implement chatbot functionality. \
                    (本WebUI基于[通义千问](https://modelscope.cn/models/qwen/Qwen-VL-Chat/)打造，实现聊天机器人功能。)'
                )
                gr.Markdown()
                gr.Markdown(
                    value='This WebUI is governed by the original license of Qwen-VL-Chat. We strongly advise users \
                    not to knowingly generate or allow others to knowingly generate harmful content, including hate \
                    speech, violence, pornography, deception, etc. \
                    (本WebUI受通义千问的许可协议限制。我们强烈建议，用户不应传播及不应允许他人传播以下内容，包括但不限于仇恨言论、暴力、\
                    色情、欺诈相关的有害信息。)'
                )
                gr.Markdown()
                dark_mode_button = gr.Button(value='🌙 Dark Mode (深色模式)')

            with gr.Column(scale=3):
                chatbot = gr.Chatbot(
                    type='tuples',
                    label='🦈 Shirley',
                    height='70vh',
                    show_copy_button=True,
                    avatar_images=(None, sh.getpath('./static/apple-touch-icon.png')),
                )
                history = gr.State(value=[])
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

            self._configure_components(
                dark_mode_button=dark_mode_button,
                chatbot=chatbot,
                history=history,
                multimodal_textbox=multimodal_textbox,
                submit_button=submit_button,
                stop_button=stop_button,
                regenerate_button=regenerate_button,
                reset_button=reset_button,
            )

            return blocks


def main() -> None:
    client = sh.Client(pretrained_model_name_or_path=sh.getpath('./models/qwen_vl_chat'))
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
