import copy

import gradio as gr
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


ChatbotTuplesInput = StateInput = list[list[str | tuple[str, str] | Component | None]] | None
ChatbotTuplesOutput = StateOutput = list[list[str | tuple[str] | tuple[str, str] | None] | tuple] | None
TextboxInput = TextboxOutput = str | None
UploadButtonInput = bytes | str | list[bytes] | list[str] | None


PRETRAINED_MODEL_PATH = shirley.config.Config().pretrained_model_path
BOX_TAG_PATTERN = r'<box>([\s\S]*?)</box>'
PUNCTUATION = '！？。＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､、〃》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘’‛“”„‟…‧﹏.'


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


def _launch_webui(model: QWenLMHeadModel, tokenizer: QWenTokenizer):
    uploaded_file_directory = os.environ.get('GRADIO_TEMP_DIR') or str(Path(tempfile.gettempdir()) / 'gradio')

    def predict(chatbot: ChatbotTuplesInput, task_history: StateInput) -> ChatbotTuplesOutput: # type: ignore
        chat_query = chatbot[-1][0]
        query = task_history[-1][0]
        print('User: ' + _parse_text(query))
        history_copy = copy.deepcopy(task_history)
        full_response = ''

        history_filter = []
        pic_index = 1
        pre = ''
        for _, [q, a] in enumerate(history_copy):
            if isinstance(q, (tuple, list)):
                q = f'Picture {pic_index}: <img>{q[0]}</img>'
                pre += q + '\n'
                pic_index += 1
            else:
                pre += q
                history_filter.append([pre, a])
                pre = ''
        history, message = history_filter[:-1], history_filter[-1][0]
        # response, history = model.chat(tokenizer, message, history=history)
        for response in model.chat_stream(tokenizer, message, history=history):
            chatbot[-1] = [_parse_text(chat_query), _remove_image_special(_parse_text(response))]
            yield chatbot
            full_response = _parse_text(response)

        response = full_response
        history.append((message, response))
        image = tokenizer.draw_bbox_on_latest_picture(response, history)
        if image is not None:
            temp_directory = secrets.token_hex(20)
            temp_directory = Path(uploaded_file_directory) / temp_directory
            temp_directory.mkdir(exist_ok=True, parents=True)
            name = f'tmp{secrets.token_hex(5)}.jpg'
            filename = temp_directory / name
            image.save(str(filename))
            chatbot.append([None, (str(filename),)])
        else:
            chatbot[-1] = [_parse_text(chat_query), response]
        # full_response = _parse_text(response)

        task_history[-1] = [query, full_response]
        print('🦈 Shirley: ' + _parse_text(full_response))
        yield chatbot

    # TODO: fix regenerate chat stream
    def regenerate(chatbot: ChatbotTuplesInput, task_history: StateInput) -> ChatbotTuplesOutput:
        if not chatbot:
            return chatbot
        if not task_history:
            return chatbot
        task_history_item = task_history[-1]
        if task_history_item[1] is None:
            return chatbot
        task_history[-1] = [task_history_item[0], None]
        chatbot_item = chatbot.pop(-1)
        if chatbot_item[0] is None:
            chatbot[-1] = [chatbot[-1][0], None]
        else:
            chatbot.append([chatbot_item[0], None])
        return predict(chatbot, task_history)

    def add_text(
        chatbot: ChatbotTuplesInput,
        task_history: StateInput,
        query: TextboxInput
    ) -> tuple[ChatbotTuplesOutput, StateOutput]:
        task_query = query
        if len(query) >= 2 and query[-1] in PUNCTUATION and query[-2] not in PUNCTUATION:
            task_query = query[:-1]
        chatbot = chatbot + [[_parse_text(query), None]]
        task_history = task_history + [[task_query, None]]
        return chatbot, task_history

    def upload_file(
        chatbot: ChatbotTuplesInput,
        task_history: StateInput,
        upload_button: UploadButtonInput
    ) -> tuple[ChatbotTuplesOutput, StateOutput]:
        chatbot = chatbot + [[(upload_button,), None]]
        task_history = task_history + [[(upload_button,), None]]
        return chatbot, task_history

    def reset_user_input() -> TextboxOutput:
        gr.update(value='')
        return None

    def reset_state(task_history: StateInput) -> ChatbotTuplesOutput:
        task_history.clear()
        return []

    with gr.Blocks(title='Shirley WebUI') as webui:
        gr.Markdown('# 🦈 Shirley WebUI')
        gr.Markdown('This WebUI is based on Qwen-VL-Chat. (本WebUI基于通义千问打造，实现聊天机器人功能。)')

        chatbot = gr.Chatbot(label='🦈 Shirley', elem_classes='control-height', height=512)
        query = gr.Textbox(lines=2, label='Input')
        task_history = gr.State([])

        with gr.Row():
            clear_button = gr.Button('🧹 Clear History (清除历史)')
            submit_button = gr.Button('🚀 Submit (发送)')
            regenerate_button = gr.Button('🤔️ Regenerate (重试)', interactive=False) # TODO: enable once fixed
            upload_button = gr.UploadButton('📁 Upload (上传文件)', file_types=['image'])

        submit_button.click(fn=add_text, inputs=[chatbot, task_history, query], outputs=[chatbot, task_history]) \
            .then(fn=predict, inputs=[chatbot, task_history], outputs=[chatbot], show_progress=True)
        submit_button.click(fn=reset_user_input, inputs=[], outputs=[query])
        clear_button.click(fn=reset_state, inputs=[task_history], outputs=[chatbot], show_progress=True)
        regenerate_button.click(fn=regenerate, inputs=[chatbot, task_history], outputs=[chatbot], show_progress=True)
        upload_button.upload(
            fn=upload_file,
            inputs=[chatbot, task_history, upload_button],
            outputs=[chatbot, task_history],
            show_progress=True
        )

    webui.queue().launch(
        share=False,
        inbrowser=False,
        server_port=8000,
        server_name='127.0.0.1',
        favicon_path=shirley.utils.getpath('./static/favicon.ico'),
    )


def main():
    generator = shirley.Generator(pretrained_model_path=PRETRAINED_MODEL_PATH)
    model = generator.model
    tokenizer = generator.tokenizer
    _launch_webui(model, tokenizer)


if __name__ == '__main__':
    main()
