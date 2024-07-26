import copy
import gradio
import pypdf
import re
import secrets
import shirley
import tempfile
from models.qwen_vl_chat.qwen_generation_utils import HistoryType
from pathlib import Path
from shirley.types import Chatbot, TaskHistory
from shirley.utils import getpath, isimage
from typing import Iterator, List, Tuple


CLIENT: shirley.Client = shirley.Client(pretrained_model_path=getpath('./models/qwen_vl_chat'))
GRADIO_TEMP_DIRECTORY: str = str(Path(tempfile.gettempdir()) / 'gradio')


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


def _load_file(file_path: str) -> str:
    if file_path.endswith('.pdf'):
        reader = pypdf.PdfReader(stream=file_path)
        return '\n'.join([page.extract_text() for page in reader.pages])
    # TODO: support more file types
    return ''


def _augment(task_history: TaskHistory) -> Tuple[str, HistoryType]:
    history = []
    picture_index = 1
    text = ''
    for _, (query, response) in enumerate(task_history):
        if isinstance(query, (Tuple, List)):
            file_path = query[0]
            if isimage(file_path):
                query = f'Picture {picture_index}: <img>{file_path}</img>'
                text += query + '\n'
                picture_index += 1
            else:
                query = _load_file(file_path=file_path)
                text += query + '\n'
        else:
            text += query
            history.append((text, response))
            text = ''
    return history[-1][0], history[:-1]


def generate(chatbot: Chatbot, task_history: TaskHistory) -> Iterator[Tuple[Chatbot, TaskHistory]]:
    chat_query = chatbot[-1][0]
    query = task_history[-1][0]
    print('User: ' + _parse_text(query))

    full_response: str = ''
    augmented_query, history = _augment(copy.deepcopy(task_history))
    for response in CLIENT.model.chat_stream(tokenizer=CLIENT.tokenizer, query=augmented_query, history=history):
        chatbot[-1] = [_parse_text(chat_query), _remove_image_special(_parse_text(response))]
        yield chatbot, task_history
        full_response = _parse_text(response)

    history.append((augmented_query, full_response))
    image = CLIENT.tokenizer.draw_bbox_on_latest_picture(response=full_response, history=history)
    if image is not None:
        image_temp_directory = secrets.token_hex(20)
        image_temp_directory = Path(GRADIO_TEMP_DIRECTORY) / image_temp_directory
        image_temp_directory.mkdir(exist_ok=True, parents=True)
        name = f'tmp{secrets.token_hex(5)}.jpg'
        filename = image_temp_directory / name
        image.save(str(filename))
        chatbot.append((None, (str(filename),)))
    else:
        chatbot[-1] = (_parse_text(chat_query), full_response)
    task_history[-1] = (query, full_response)

    print('🦈 Shirley: ' + _parse_text(full_response))
    yield chatbot, task_history


def regenerate(chatbot: Chatbot, task_history: TaskHistory) -> Tuple[Chatbot, TaskHistory]:
    if not chatbot or not task_history:
        return chatbot, task_history
    task_history_item = task_history[-1]
    if task_history_item[1] is None:
        return chatbot, task_history
    task_history[-1] = (task_history_item[0], None)
    chatbot_item = chatbot.pop(-1)
    if chatbot_item[0] is None:
        chatbot[-1] = (chatbot[-1][0], None)
    else:
        chatbot.append((chatbot_item[0], None))
    return chatbot, task_history


def submit(chatbot: Chatbot, task_history: TaskHistory, query: str) -> Tuple[Chatbot, TaskHistory]:
    chatbot = chatbot + [(_parse_text(query), None)]
    task_history = task_history + [(query, None)]
    return chatbot, task_history


def upload(chatbot: Chatbot, task_history: TaskHistory, upload_button: str) -> Tuple[Chatbot, TaskHistory]:
    chatbot = chatbot + [((upload_button,), None)]
    task_history = task_history + [((upload_button,), None)]
    return chatbot, task_history


def reset_input() -> str:
    return ''


def clear() -> Tuple[Chatbot, TaskHistory]:
    return [], []


def main() -> None:
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
            clear_button = gradio.Button('🧹 Clear (清除历史)')
            submit_button = gradio.Button('🚀 Submit (发送)')
            regenerate_button = gradio.Button('🤔️ Regenerate (重试)')
            upload_button = gradio.UploadButton('📁 Upload (上传文件)', file_types=['file'])

        submit_button.click(
            fn=submit,
            inputs=[chatbot, task_history, query],
            outputs=[chatbot, task_history],
        ) \
        .then(
            fn=generate,
            inputs=[chatbot, task_history],
            outputs=[chatbot, task_history],
            show_progress=True,
        )

        submit_button.click(
            fn=reset_input,
            inputs=None,
            outputs=query,
        )

        clear_button.click(
            fn=clear,
            inputs=None,
            outputs=[chatbot, task_history],
            show_progress=True,
        )

        regenerate_button.click(
            fn=regenerate,
            inputs=[chatbot, task_history],
            outputs=[chatbot, task_history],
            show_progress=True,
        ) \
        .then(
            fn=generate,
            inputs=[chatbot, task_history],
            outputs=[chatbot, task_history],
            show_progress=True,
        )

        upload_button.upload(
            fn=upload,
            inputs=[chatbot, task_history, upload_button],
            outputs=[chatbot, task_history],
            show_progress=True,
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
        favicon_path=getpath('./static/favicon.ico'),
    )


if __name__ == '__main__':
    main()
