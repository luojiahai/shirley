import gradio as gr
import logging
import pypdf
import shirley as sh
import sys
from .interface import Interface
from gradio.events import Dependency
from typing import Callable, Iterator, List, Tuple


logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


class Chat(Interface):

    def __init__(self, local: bool = True, *args, **kwargs) -> None:
        super().__init__()

        self._client: sh.clients.Chat = sh.clients.Chat(local=local)
        self._pretrained_models: List[str] = self._client.get_models()
        self._pretrained_model_name_or_path: str = self._client.get_model_name_or_path(
            model_name=self._pretrained_models[0],
        )
        self._generating: bool = False
        self._history: List[Tuple] = []

        self._make_components(*args, **kwargs)


    @property
    def client(self) -> sh.clients.Chat:
        return self._client


    def _load_context(self, filepath: str) -> str:
        if sh.utils.isimage(filepath):
            return f'Picture: <img>{filepath}</img>'
        elif filepath.endswith('.pdf'):
            reader = pypdf.PdfReader(stream=filepath)
            return '\n'.join([page.extract_text() for page in reader.pages])
        else:
            logger.warning(f'File type {filepath} not supported.')
            return ''


    def _get_query_and_history(self) -> Tuple[sh.types.QwenQuery, sh.types.QwenHistory]:
        history: sh.types.QwenHistory = []
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


    def _pregenerate(self, *args, **kwargs) -> sh.types.GradioComponents:
        components = [
            gr.MultimodalTextbox(interactive=False),
            gr.Button(variant='secondary', interactive=False),
            gr.Button(variant='stop', interactive=True),
            gr.Button(interactive=False),
            gr.ClearButton(interactive=False),
        ]
        return tuple(components)


    def _generate(self, *args, **kwargs) -> Iterator[sh.types.ChatbotTuplesOutput]:
        chatbot: sh.types.ChatbotTuplesInput = args[0]

        self._generating = True
        logger.info(f'😀 User: {chatbot[-1][0]}')

        query, history = self._get_query_and_history()
        full_response = ''
        for response in self._client.chat_stream(query=query, history=history):
            if not self._generating: break
            chatbot[-1] = (chatbot[-1][0], sh.utils.parse(text=response, remove_image_tags=True))
            yield chatbot
            full_response = sh.utils.parse(text=response)

        history.append((query, full_response))
        image_filepath = self._client.draw_bbox_on_latest_picture(history=history)
        if image_filepath is not None:
            chatbot.append((None, (image_filepath,)))
        else:
            chatbot[-1] = (chatbot[-1][0], full_response)
        self._history[-1] = (self._history[-1][0], full_response)

        logger.info(f'🦈 Shirley: {full_response}')
        self._generating = False
        yield chatbot


    def _postgenerate(self, *args, **kwargs) -> sh.types.GradioComponents:
        components = [
            gr.MultimodalTextbox(interactive=True),
            gr.Button(variant='secondary', interactive=False),
            gr.Button(variant='secondary', interactive=False),
            gr.Button(interactive=True),
            gr.ClearButton(interactive=True),
        ]
        return tuple(components)


    def _validate(self, *args, **kwargs) -> None:
        if not self._client.model:
            logger.error('Model not loaded.')
            raise gr.Error('Model not loaded. Please load a model.')


    def _submit(self, *args, **kwargs) -> Tuple[sh.types.ChatbotTuplesOutput, sh.types.MultimodalTextboxOutput]:
        chatbot: sh.types.ChatbotTuplesInput = args[0]
        multimodal_textbox: sh.types.MultimodalTextboxInput = args[1]

        text = multimodal_textbox['text']
        if not text or not text.strip():
            raise gr.Error('Text not valid.')

        for filepath in multimodal_textbox['files']:
            chatbot = chatbot + [((filepath,), None)]
            self._history = self._history + [((filepath,), None)]

        if multimodal_textbox['text'] is not None:
            chatbot = chatbot + [(sh.utils.parse(text=multimodal_textbox['text']), None)]
            self._history = self._history + [(multimodal_textbox['text'], None)]

        return chatbot, None


    def _stop(self, *args, **kwargs) -> sh.types.GradioComponents:
        self._generating = False


    def _regenerate(self, *args, **kwargs) -> sh.types.ChatbotTuplesOutput | Iterator[sh.types.ChatbotTuplesOutput]:
        chatbot: sh.types.ChatbotTuplesInput = args[0]

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


    def _reset(self, *args, **kwargs) -> sh.types.GradioComponents:
        self._history = []

        components = [
            gr.MultimodalTextbox(interactive=True),
            gr.Button(variant='secondary', interactive=False),
            gr.Button(variant='secondary', interactive=False),
            gr.Button(interactive=False),
            gr.ClearButton(interactive=False),
        ]
        return tuple(components)


    def _model_dropdown_change(self, *args, **kwargs) -> None:
        model_dropdown: sh.types.DropdownInput = args[0]

        self._pretrained_model_name_or_path = self._client.get_model_name_or_path(model_name=model_dropdown)


    def _load_button_click(self, *args, **kwargs) -> sh.types.GradioComponents:
        self._client.load_model(pretrained_model_name_or_path=self._pretrained_model_name_or_path)
        gr.Info(message='Model loaded.')

        return gr.Dropdown(interactive=True), gr.Button(interactive=True)


    def _multimodal_textbox_change(self, *args, **kwargs) -> sh.types.GradioComponents:
        multimodal_textbox: sh.types.MultimodalTextboxInput = args[0]

        text = multimodal_textbox['text']
        if not text or not text.strip():
            return gr.Button(variant='secondary', interactive=False)

        return gr.Button(variant='primary', interactive=True)


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
        model_config: gr.JSON = kwargs['model_config']

        preload = load_button.click(
            fn=lambda: (gr.Dropdown(interactive=False), gr.Button(interactive=False)),
            inputs=None,
            outputs=[model_dropdown, load_button],
            show_api=False,
        )
        load_button_click = preload.then(
            fn=self._load_button_click,
            inputs=None,
            outputs=[model_dropdown, load_button],
            show_api=False,
        )
        load_button_click.then(
            fn=lambda: self._client.get_model_config(),
            inputs=None,
            outputs=[model_config],
            show_api=False,
        )


    def _set_event_trigger_generate(self, dependency: Dependency, fn: Callable, *args, **kwargs) -> None:
        chatbot: gr.Chatbot = kwargs['chatbot']
        multimodal_textbox: gr.MultimodalTextbox = kwargs['multimodal_textbox']
        submit_button: gr.Button = kwargs['submit_button']
        stop_button: gr.Button = kwargs['stop_button']
        regenerate_button: gr.Button = kwargs['regenerate_button']
        reset_button: gr.ClearButton = kwargs['reset_button']

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
        reset_button: gr.ClearButton = kwargs['reset_button']

        reset_button.add(components=[chatbot, multimodal_textbox])

        reset_button.click(
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


    def _make_components(self, *args, **kwargs) -> None:
        avatar_images: Tuple | None = kwargs.get('avatar_images', None)

        with gr.Row():
            with gr.Column(scale=1):
                with gr.Group():
                    model_dropdown = gr.Dropdown(
                        choices=self._pretrained_models,
                        value=self._pretrained_models[0],
                        multiselect=False,
                        allow_custom_value=False,
                        label='🤗 Model (模型)',
                    )
                    load_button = gr.Button(value='📥 Load (加载)', variant='secondary')
                model_config = gr.JSON(show_label=False, scale=1)

            with gr.Column(scale=3):
                chatbot = gr.Chatbot(
                    show_label=False,
                    height='50vh',
                    show_copy_button=True,
                    avatar_images=avatar_images,
                )
                multimodal_textbox = gr.MultimodalTextbox(
                    placeholder='✏️ Enter text or upload file… (输入文字或者上传文件…)',
                    show_label=False,
                    interactive=True,
                )
                with gr.Row():
                    submit_button = gr.Button(value='🚀 Submit (发送)', variant='secondary', interactive=False)
                    stop_button = gr.Button(value='⏹️ Stop (停止)', variant='secondary', interactive=False)
                    regenerate_button = gr.Button(value='🔁 Regenerate (重新生成)', interactive=False)
                    reset_button = gr.ClearButton(value='🧹 Reset (重置)', interactive=False)

        self._setup(
            model_dropdown=model_dropdown,
            load_button=load_button,
            model_config=model_config,
            chatbot=chatbot,
            multimodal_textbox=multimodal_textbox,
            submit_button=submit_button,
            stop_button=stop_button,
            regenerate_button=regenerate_button,
            reset_button=reset_button,
        )
