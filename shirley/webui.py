import copy
import gradio
import pypdf
import re
import shirley
import tempfile
import uuid
from models.qwen_vl_chat.qwen_generation_utils import HistoryType
from pathlib import Path
from shirley.types import Chatbot, HistoryState
from shirley.utils import getpath, isimage
from typing import Iterator, List, Tuple


CLIENT: shirley.Client = shirley.Client(pretrained_model_path=getpath('./models/qwen_vl_chat'))
GRADIO_TEMP_DIRECTORY: str = str(Path(tempfile.gettempdir()) / 'gradio')


def _parse(text: str) -> str:
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


def _parse_and_remove_tags(text: str) -> str:
    text = _parse(text)
    text = text.replace('<ref>', '').replace('</ref>', '')
    return re.sub(r'<box>.*?(</box>|$)', '', text)


def _get_context(filepath: str) -> str:
    if isimage(filepath):
        return f'Picture: <img>{filepath}</img>'
    elif filepath.endswith('.pdf'):
        reader = pypdf.PdfReader(stream=filepath)
        return '\n'.join([page.extract_text() for page in reader.pages])
    # TODO: support more file types
    return ''


def _augment(state: HistoryState) -> Tuple[str, HistoryType]:
    history = []
    current_query = ''
    for _, (raw_query, response) in enumerate(state):
        if isinstance(raw_query, (Tuple, List)):
            filepath = raw_query[0]
            context = _get_context(filepath=filepath)
            current_query += context + '\n'
        else:
            current_query += raw_query
            history.append((current_query, response))
            current_query = ''
    return history[-1][0], history[:-1]


def generate(chatbot: Chatbot, state: HistoryState) -> Iterator[Tuple[Chatbot, HistoryState]]:
    chat_query = chatbot[-1][0]
    print('User: ' + chat_query)

    query, history = _augment(copy.deepcopy(state))
    for response in CLIENT.model.chat_stream(tokenizer=CLIENT.tokenizer, query=query, history=history):
        chatbot[-1] = (chat_query, _parse_and_remove_tags(response))
        yield chatbot, state
        full_response = _parse(response)

    history.append((query, full_response))
    image = CLIENT.tokenizer.draw_bbox_on_latest_picture(response=full_response, history=history)
    if image is not None:
        temp_directory = Path(GRADIO_TEMP_DIRECTORY) / 'images'
        temp_directory.mkdir(exist_ok=True, parents=True)
        name = f'tmp-{uuid.uuid4()}.jpg'
        filename = temp_directory / name
        image.save(str(filename))
        chatbot.append((None, (str(filename),)))
    else:
        chatbot[-1] = (chat_query, full_response)
    state[-1][1] = full_response

    print('🦈 Shirley: ' + full_response)
    yield chatbot, state


def regenerate(chatbot: Chatbot, state: HistoryState) -> Tuple[Chatbot, HistoryState]:
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


def submit(chatbot: Chatbot, state: HistoryState, raw_query: str) -> Tuple[Chatbot, HistoryState]:
    chatbot = chatbot + [(_parse(raw_query), None)]
    state = state + [(raw_query, None)]
    return chatbot, state


def upload(chatbot: Chatbot, state: HistoryState, filepath: str) -> Tuple[Chatbot, HistoryState]:
    chatbot = chatbot + [((filepath,), None)]
    state = state + [((filepath,), None)]
    return chatbot, state


def reset_input() -> str:
    return ''


def clear() -> Tuple[Chatbot, HistoryState]:
    return [], []


def main() -> None:
    with gradio.Blocks(title='Shirley WebUI', fill_height=True) as webui:
        gradio.Markdown('# 🦈 Shirley WebUI')
        gradio.Markdown(
            'This WebUI is based on [Qwen-VL-Chat](https://modelscope.cn/models/qwen/Qwen-VL-Chat/) to implement \
            chatbot functionality. \
            (本WebUI基于[通义千问](https://modelscope.cn/models/qwen/Qwen-VL-Chat/)打造，实现聊天机器人功能。)'
        )

        chatbot = gradio.Chatbot(label='🦈 Shirley')
        textbox = gradio.Textbox(lines=2, label='Input (输入)')
        state = gradio.State([])

        with gradio.Row():
            submit_button = gradio.Button('🚀 Submit (发送)')
            regenerate_button = gradio.Button('🤔️ Regenerate (重试)')
            upload_button = gradio.UploadButton('📁 Upload (上传文件)', file_count='single', file_types=['file'])
            clear_button = gradio.Button('🧹 Clear (清除历史)')

        submit_button.click(
            fn=submit,
            inputs=[chatbot, state, textbox],
            outputs=[chatbot, state],
        ) \
        .then(
            fn=generate,
            inputs=[chatbot, state],
            outputs=[chatbot, state],
            show_progress=True,
        )

        submit_button.click(
            fn=reset_input,
            inputs=None,
            outputs=textbox,
        )

        clear_button.click(
            fn=clear,
            inputs=None,
            outputs=[chatbot, state],
            show_progress=True,
        )

        regenerate_button.click(
            fn=regenerate,
            inputs=[chatbot, state],
            outputs=[chatbot, state],
            show_progress=True,
        ) \
        .then(
            fn=generate,
            inputs=[chatbot, state],
            outputs=[chatbot, state],
            show_progress=True,
        )

        upload_button.upload(
            fn=upload,
            inputs=[chatbot, state, upload_button],
            outputs=[chatbot, state],
            show_progress=True,
        )

        gradio.Markdown(
            '<font size=2>Note: This WebUI is governed by the original license of Qwen-VL-Chat. We strongly advise \
            users not to knowingly generate or allow others to knowingly generate harmful content, including hate \
            speech, violence, pornography, deception, etc. \
            (注：本WebUI受通义千问的许可协议限制。我们强烈建议，用户不应传播及不应允许他人传播以下内容，包括但不限于仇恨言论、暴力、色情、\
            欺诈相关的有害信息。)'
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
