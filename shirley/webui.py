import copy
import gradio
import os
import re
import secrets
import shirley
import shirley.config
import shirley.utils
import tempfile
from gradio.components import Component
from models.qwen_vl_chat.modeling_qwen import QWenLMHeadModel
from models.qwen_vl_chat.tokenization_qwen import QWenTokenizer
from pathlib import Path
from PIL import Image


ChatbotTuplesInput = TaskHistoryInput = list[list[str | tuple[str, str] | Component | None]] | None
ChatbotTuplesOutput = TaskHistoryOutput = list[list[str | tuple[str] | tuple[str, str] | None] | tuple] | None
TextboxInput = TextboxOutput = str | None
UploadButtonInput = bytes | str | list[bytes] | list[str] | None


PRETRAINED_MODEL_PATH = shirley.config.Config().pretrained_model_path
PUNCTUATION = '！？。＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､、〃》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟\
    〰〾〿–—‘’‛“”„‟…‧﹏.'


def _parse_text(text: str) -> str:
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
    text = ''.join(lines)
    return text


def _remove_image_special(text: str) -> str:
    text = text.replace('<ref>', '').replace('</ref>', '')
    return re.sub(r'<box>.*?(</box>|$)', '', text)


def _is_valid_image(file_path: str) -> bool:
    try:
        with Image.open(file_path) as img:
            img.verify()
            return True
    except (IOError, SyntaxError):
        return False
    

def _augment(task_history: TaskHistoryInput) -> tuple[TaskHistoryOutput, str]:
    history_filter = []
    picture_index = 1
    text = ''
    for _, [query, response] in enumerate(task_history):
        if isinstance(query, (tuple, list)):
            if _is_valid_image(query[0]):
                query = f'Picture {picture_index}: <img>{query[0]}</img>'
                text += query + '\n'
                picture_index += 1
            else:
                # TODO: other file types
                pass
        else:
            text += query
            history_filter.append([text, response])
            text = ''
    return history_filter[:-1], history_filter[-1][0]


def _launch_webui(model: QWenLMHeadModel, tokenizer: QWenTokenizer) -> None:
    uploaded_file_directory = os.environ.get('GRADIO_TEMP_DIR') or str(Path(tempfile.gettempdir()) / 'gradio')

    def generate(
        chatbot: ChatbotTuplesInput,
        task_history: TaskHistoryInput
    ) -> tuple[ChatbotTuplesOutput, TaskHistoryOutput]: # type: ignore
        chat_query = chatbot[-1][0]
        query = task_history[-1][0]
        print('User: ' + _parse_text(query))

        full_response: str = ''
        history, message = _augment(copy.deepcopy(task_history))
        for response in model.chat_stream(tokenizer=tokenizer, query=message, history=history):
            chatbot[-1] = [_parse_text(chat_query), _remove_image_special(_parse_text(response))]
            yield chatbot, task_history
            full_response = _parse_text(response)
        history.append([message, full_response])

        image = tokenizer.draw_bbox_on_latest_picture(response=full_response, history=history)
        if image is not None:
            temp_directory = secrets.token_hex(20)
            temp_directory = Path(uploaded_file_directory) / temp_directory
            temp_directory.mkdir(exist_ok=True, parents=True)
            name = f'tmp{secrets.token_hex(5)}.jpg'
            filename = temp_directory / name
            image.save(str(filename))
            chatbot.append([None, (str(filename),)])
        else:
            chatbot[-1] = [_parse_text(chat_query), full_response]
        task_history[-1] = [query, full_response]

        print('🦈 Shirley: ' + _parse_text(full_response))
        yield chatbot, task_history

    def regenerate(
        chatbot: ChatbotTuplesInput,
        task_history: TaskHistoryInput
    ) -> tuple[ChatbotTuplesOutput, TaskHistoryOutput]:
        if not chatbot:
            return chatbot, task_history
        if not task_history:
            return chatbot, task_history
        task_history_item = task_history[-1]
        if task_history_item[1] is None:
            return chatbot, task_history
        task_history[-1] = [task_history_item[0], None]
        chatbot_item = chatbot.pop(-1)
        if chatbot_item[0] is None:
            chatbot[-1] = [chatbot[-1][0], None]
        else:
            chatbot.append([chatbot_item[0], None])
        return chatbot, task_history

    def add_text(
        chatbot: ChatbotTuplesInput,
        task_history: TaskHistoryInput,
        query: TextboxInput
    ) -> tuple[ChatbotTuplesOutput, TaskHistoryOutput]:
        task_query = query
        if len(query) >= 2 and query[-1] in PUNCTUATION and query[-2] not in PUNCTUATION:
            task_query = query[:-1]
        chatbot = chatbot + [[_parse_text(query), None]]
        task_history = task_history + [[task_query, None]]
        return chatbot, task_history

    def upload_file(
        chatbot: ChatbotTuplesInput,
        task_history: TaskHistoryInput,
        upload_button: UploadButtonInput
    ) -> tuple[ChatbotTuplesOutput, TaskHistoryOutput]:
        chatbot = chatbot + [[(upload_button,), None]]
        task_history = task_history + [[(upload_button,), None]]
        return chatbot, task_history

    def reset_user_input() -> TextboxOutput:
        gradio.update(value='')
        return None

    def clear() -> tuple[ChatbotTuplesOutput, TaskHistoryOutput]:
        return [], []

    with gradio.Blocks(title='Shirley WebUI') as webui:
        gradio.Markdown('# 🦈 Shirley WebUI')
        gradio.Markdown(
            'This WebUI is based on [Qwen-VL-Chat](https://modelscope.cn/models/qwen/Qwen-VL-Chat/) to implement \
            chatbot functionality. \
            (本WebUI基于[通义千问](https://modelscope.cn/models/qwen/Qwen-VL-Chat/)打造，实现聊天机器人功能。)'
        )

        chatbot = gradio.Chatbot(label='🦈 Shirley', elem_classes='control-height', height=750)
        query = gradio.Textbox(lines=2, label='Input')
        task_history = gradio.State([])

        with gradio.Row():
            clear_button = gradio.Button('🧹 Clear History (清除历史)')
            submit_button = gradio.Button('🚀 Submit (发送)')
            regenerate_button = gradio.Button('🤔️ Regenerate (重试)')
            upload_button = gradio.UploadButton('📁 Upload (上传文件)', file_types=['file'])

        submit_clicked = submit_button.click(
            fn=add_text,
            inputs=[chatbot, task_history, query],
            outputs=[chatbot, task_history]
        )
        submit_clicked.then(
            fn=generate,
            inputs=[chatbot, task_history],
            outputs=[chatbot, task_history],
            show_progress=True
        )

        submit_button.click(
            fn=reset_user_input,
            inputs=None,
            outputs=[query]
        )

        clear_button.click(
            fn=clear,
            inputs=None,
            outputs=[chatbot, task_history],
            show_progress=True
        )

        regenerate_clicked = regenerate_button.click(
            fn=regenerate,
            inputs=[chatbot, task_history],
            outputs=[chatbot, task_history],
            show_progress=True
        )
        regenerate_clicked.then(
            fn=generate,
            inputs=[chatbot, task_history],
            outputs=[chatbot, task_history],
            show_progress=True
        )

        upload_button.upload(
            fn=upload_file,
            inputs=[chatbot, task_history, upload_button],
            outputs=[chatbot, task_history],
            show_progress=True
        )

        gradio.Markdown(
            '<font size=2>Note: This WebUI is governed by the original license of Qwen-VL-Chat. We strongly advise \
            users not to knowingly generate or allow others to knowingly generate harmful content, including hate \
            speech, violence, pornography, deception, etc. \
            (注：本WebUI受通义千问的许可协议限制。我们强烈建议，用户不应传播及不应允许他人传播以下内容，包括但不限于仇恨言论、\
            暴力、色情、欺诈相关的有害信息。)'
        )

    webui.queue().launch(
        share=False,
        inbrowser=False,
        server_port=8000,
        server_name='127.0.0.1',
        favicon_path=shirley.utils.getpath('./static/favicon.ico'),
    )


def main() -> None:
    generator = shirley.Generator(pretrained_model_path=PRETRAINED_MODEL_PATH)
    model = generator.model
    tokenizer = generator.tokenizer
    _launch_webui(model, tokenizer)


if __name__ == '__main__':
    main()
