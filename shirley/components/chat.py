import gradio as gr
import logging
import os
import pypdf
import re
import shirley as sh
import sys
from gradio.events import Dependency
from typing import Callable, Iterator, List, Tuple


logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


class ChatComponent(sh.Component):

    MODELS_PATH = './models'


    def __init__(self) -> None:
        super().__init__()
        self._pretrained_models: List[str] = self._get_available_pretrained_models()
        self._pretrained_model_name_or_path: str | None = None
        self._client: sh.Client | None = None
        self._generating: bool = False
        self._history: List[Tuple] = []


    def _get_available_pretrained_models(self) -> List[str]:
        models_directory = os.path.abspath(os.path.expanduser(self.MODELS_PATH))
        pretrained_models = os.listdir(models_directory)
        return pretrained_models


    def _get_pretrained_model_path(self, model_directory: str) -> str:
        return os.path.abspath(os.path.expanduser(f'{self.MODELS_PATH}/{model_directory}'))


    def _parse(self, text: str, remove_image_tags: bool = False) -> str:
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


    def _load_context(self, filepath: str) -> str:
        if sh.isimage(filepath):
            return f'Picture: <img>{filepath}</img>'
        elif filepath.endswith('.pdf'):
            reader = pypdf.PdfReader(stream=filepath)
            return '\n'.join([page.extract_text() for page in reader.pages])
        else:
            logger.warning(f'File type {filepath} not supported.')
            return ''


    def _get_query_and_history(self) -> Tuple[str, sh.QwenHistory]:
        history: sh.QwenHistory = []
        text = ''
        for _, (query, response) in enumerate(self._history):
            if isinstance(query, (Tuple, List)):
                filepath = query[0]
                context = self._load_context(filepath=filepath)
                text += context + '\n'
            else:
                text += query
                history.append((text, response))
                text = ''
        return history[-1][0], history[:-1]


    def _pregenerate(self, *args, **kwargs) -> sh.GradioComponents:
        components = [
            gr.MultimodalTextbox(interactive=False),
            gr.Button(variant='secondary', interactive=False),
            gr.Button(variant='stop', interactive=True),
            gr.Button(interactive=False),
            gr.Button(interactive=False),
        ]
        return tuple(components)


    def _generate(self, *args, **kwargs) -> Iterator[sh.ChatbotTuplesOutput]:
        chatbot: sh.ChatbotTuplesInput = args[0]

        self._generating = True
        logger.info(f'🙂 User: {chatbot[-1][0]}')

        query, history = self._get_query_and_history()
        full_response = ''
        for response in self._client.chat_stream(query=query, history=history):
            if not self._generating: break
            chatbot[-1] = (chatbot[-1][0], self._parse(text=response, remove_image_tags=True))
            yield chatbot
            full_response = self._parse(text=response)

        history.append((query, full_response))
        image_filepath = self._client.draw_bbox_on_latest_picture(history=history, tempdir=self.tempdir)
        if image_filepath is not None:
            chatbot.append((None, (image_filepath,)))
        else:
            chatbot[-1] = (chatbot[-1][0], full_response)
        self._history[-1] = (self._history[-1][0], full_response)

        logger.info(f'🦈 Shirley: {full_response}')
        self._generating = False
        yield chatbot


    def _postgenerate(self, *args, **kwargs) -> sh.GradioComponents:
        components = [
            gr.MultimodalTextbox(interactive=True),
            gr.Button(variant='secondary', interactive=False),
            gr.Button(variant='secondary', interactive=False),
            gr.Button(interactive=True),
            gr.Button(interactive=True),
        ]
        return tuple(components)


    def _validate(self, *args, **kwargs) -> None:
        if not self._client:
            logger.error('Model not loaded.')
            raise gr.Error('Pre-trained model not loaded. Please load a model.')


    def _submit(self, *args, **kwargs) -> Tuple[sh.ChatbotTuplesOutput, sh.MultimodalTextboxOutput]:
        chatbot: sh.ChatbotTuplesInput = args[0]
        multimodal_textbox: sh.MultimodalTextboxInput = args[1]

        text = multimodal_textbox['text']
        if not text or not text.strip():
            raise gr.Error(visible=False)

        for filepath in multimodal_textbox['files']:
            chatbot = chatbot + [((filepath,), None)]
            self._history = self._history + [((filepath,), None)]

        if multimodal_textbox['text'] is not None:
            chatbot = chatbot + [(self._parse(text=multimodal_textbox['text']), None)]
            self._history = self._history + [(multimodal_textbox['text'], None)]

        return chatbot, None


    def _stop(self, *args, **kwargs) -> sh.GradioComponents:
        self._generating = False


    def _regenerate(self, *args, **kwargs) -> sh.ChatbotTuplesOutput | Iterator[sh.ChatbotTuplesOutput]:
        chatbot: sh.ChatbotTuplesInput = args[0]

        if len(chatbot) < 1 or len(self._history) < 1:
            return chatbot

        history_last = self._history[-1]
        if history_last[1] is None:
            return chatbot
        self._history[-1] = (history_last[0], None)

        chatbot_last = chatbot.pop(-1)
        if chatbot_last[0] is None:
            chatbot[-1] = (chatbot[-1][0], None)
        else:
            chatbot.append((chatbot_last[0], None))

        yield from self._generate(*args, **kwargs)


    def _reset(self, *args, **kwargs) -> sh.GradioComponents:
        components = [
            gr.MultimodalTextbox(interactive=True),
            gr.Button(variant='secondary', interactive=False),
            gr.Button(variant='secondary', interactive=False),
            gr.Button(interactive=False),
            gr.Button(interactive=False),
        ]
        return tuple(components)
    

    def _model_dropdown_change(self, *args, **kwargs) -> None:
        model_dropdown: sh.DropdownInput = args[0]

        self._pretrained_model_name_or_path = self._get_pretrained_model_path(model_directory=model_dropdown)


    def _load_button_click(self, *args, **kwargs) -> sh.GradioComponents:
        self._client = sh.Client(pretrained_model_name_or_path=self._pretrained_model_name_or_path)

        return gr.Dropdown(interactive=True), gr.Button(interactive=True)


    def _multimodal_textbox_change(self, *args, **kwargs) -> sh.GradioComponents:
        multimodal_textbox: sh.MultimodalTextboxInput = args[0]

        text = multimodal_textbox['text']
        if not text or not text.strip():
            return gr.Button(variant='secondary', interactive=False)

        return gr.Button(variant='primary', interactive=True)
    

    def _reset_button_click(self, *args, **kwargs) -> Tuple[sh.ChatbotTuplesOutput, sh.MultimodalTextboxOutput]:
        self._history = []
        return [], None


    def _setup_model_dropdown(self, *args, **kwargs) -> None:
        model_dropdown: gr.Dropdown = kwargs['model_dropdown']

        model_dropdown.change(
            fn=self._model_dropdown_change,
            inputs=[model_dropdown],
            outputs=None,
            show_api=False,
        )


    def _setup_load_button(self, *args, **kwargs) -> None:
        model_dropdown: gr.Dropdown = kwargs['model_dropdown']
        load_button: gr.Button = kwargs['load_button']

        load_button_click = load_button.click(
            fn=lambda: (gr.Dropdown(interactive=False), gr.Button(interactive=False)),
            inputs=None,
            outputs=[model_dropdown, load_button],
            show_api=False,
        )
        load_button_click.then(
            fn=self._load_button_click,
            inputs=None,
            outputs=[model_dropdown, load_button],
            show_api=False,
        )


    def _set_event_trigger_generate(self, dependency: Dependency, fn: Callable, *args, **kwargs) -> None:
        chatbot: gr.Chatbot = kwargs['chatbot']
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
            inputs=[chatbot],
            outputs=[chatbot],
            show_progress=True,
            show_api=False,
        )
        generate.then(
            fn=self._postgenerate,
            inputs=None,
            outputs=[multimodal_textbox, submit_button, stop_button, regenerate_button, reset_button],
            show_api=False,
        )


    def _setup_multimodal_textbox(self, *args, **kwargs) -> None:
        chatbot: gr.Chatbot = kwargs['chatbot']
        multimodal_textbox: gr.MultimodalTextbox = kwargs['multimodal_textbox']
        submit_button: gr.Button = kwargs['submit_button']

        multimodal_textbox.change(
            fn=self._multimodal_textbox_change,
            inputs=[multimodal_textbox],
            outputs=[submit_button],
            show_api=False,
        )

        validate = multimodal_textbox.submit(
            fn=self._validate,
            show_api=False,
        )
        submit = validate.success(
            fn=self._submit,
            inputs=[chatbot, multimodal_textbox],
            outputs=[chatbot, multimodal_textbox],
            show_api=False,
        )
        self._set_event_trigger_generate(dependency=submit, fn=self._generate, *args, **kwargs)


    def _setup_submit_button(self, *args, **kwargs) -> None:
        chatbot: gr.Chatbot = kwargs['chatbot']
        multimodal_textbox: gr.MultimodalTextbox = kwargs['multimodal_textbox']
        submit_button: gr.Button = kwargs['submit_button']

        validate = submit_button.click(
            fn=self._validate,
            show_api=False,
        )
        submit = validate.success(
            fn=self._submit,
            inputs=[chatbot, multimodal_textbox],
            outputs=[chatbot, multimodal_textbox],
            show_api=False,
        )
        self._set_event_trigger_generate(dependency=submit, fn=self._generate, *args, **kwargs)


    def _setup_stop_button(self, *args, **kwargs) -> None:
        stop_button: gr.Button = kwargs['stop_button']

        stop_button.click(fn=self._stop, show_api=False)


    def _setup_regenerate_button(self, *args, **kwargs) -> None:
        regenerate_button: gr.Button = kwargs['regenerate_button']

        click = regenerate_button.click(fn=lambda:None, show_api=False)
        self._set_event_trigger_generate(dependency=click, fn=self._regenerate, *args, **kwargs)


    def _setup_reset_button(self, *args, **kwargs) -> None:
        chatbot: gr.Chatbot = kwargs['chatbot']
        multimodal_textbox: gr.MultimodalTextbox = kwargs['multimodal_textbox']
        submit_button: gr.Button = kwargs['submit_button']
        stop_button: gr.Button = kwargs['stop_button']
        regenerate_button: gr.Button = kwargs['regenerate_button']
        reset_button: gr.Button = kwargs['reset_button']

        reset_button_click = reset_button.click(
            fn=self._reset_button_click,
            inputs=None,
            outputs=[chatbot, multimodal_textbox],
            show_api=False,
        )
        reset_button_click.then(
            fn=self._reset,
            inputs=None,
            outputs=[multimodal_textbox, submit_button, stop_button, regenerate_button, reset_button],
            show_api=False,
        )


    def _setup(self, *args, **kwargs) -> None:
        self._setup_model_dropdown(*args, **kwargs)
        self._setup_load_button(*args, **kwargs)
        self._setup_multimodal_textbox(*args, **kwargs)
        self._setup_submit_button(*args, **kwargs)
        self._setup_stop_button(*args, **kwargs)
        self._setup_regenerate_button(*args, **kwargs)
        self._setup_reset_button(*args, **kwargs)


    def make_components(self, *args, **kwargs) -> None:
        gr.Markdown(value='### 🦈 Chat')
        gr.Markdown(
            value='This is based on [Qwen-VL-Chat](https://modelscope.cn/models/qwen/Qwen-VL-Chat/) \
            to implement chatbot functionality. \
            (此基于[通义千问](https://modelscope.cn/models/qwen/Qwen-VL-Chat/)打造，实现聊天机器人功能。)'
        )

        with gr.Row():
            with gr.Column(scale=1, variant='panel'):
                self._pretrained_model_name_or_path = self._get_pretrained_model_path(
                    model_directory=self._pretrained_models[0],
                )
                with gr.Group():
                    model_dropdown = gr.Dropdown(
                        choices=self._pretrained_models,
                        value=self._pretrained_models[0],
                        multiselect=False,
                        label='📦 Pre-trained Model (预训练模型)',
                        interactive=True,
                    )
                    load_button = gr.Button(value='📥 Load (读取)', variant='secondary')

            with gr.Column(scale=3, variant='panel'):
                chatbot = gr.Chatbot(
                    type='tuples',
                    label='🦈 Shirley',
                    height='50vh',
                    show_copy_button=True,
                    avatar_images=(None, sh.getpath('./static/apple-touch-icon.png')),
                )
                with gr.Group():
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

        gr.Markdown(
            '<font size=2>Note: This is governed by the original license of Qwen-VL-Chat. We strongly advise users not \
            to knowingly generate or allow others to knowingly generate harmful content, including hate speech, \
            violence, pornography, deception, etc. \
            (注：此受通义千问的许可协议限制。我们强烈建议，用户不应传播及不应允许他人传播以下内容，包括但不限于仇恨言论、暴力、\
            色情、欺诈相关的有害信息。)'
        )

        self._setup(
            model_dropdown=model_dropdown,
            load_button=load_button,
            chatbot=chatbot,
            multimodal_textbox=multimodal_textbox,
            submit_button=submit_button,
            stop_button=stop_button,
            regenerate_button=regenerate_button,
            reset_button=reset_button,
        )
