## 🦈 Shirley

It is just doing some stuff intelligently. It has the following features:
- Chat, powered by [Qwen/Qwen-VL-Chat](https://huggingface.co/Qwen/Qwen-VL-Chat) (通义千问).
- Text-To-Speech, powered by [Azure AI Speech](https://azure.microsoft.com/products/ai-services/ai-speech).

### Installation

```bash
pip install shirley
```

### Quick tour

```python
import shirley as sh

header = sh.interfaces.Header()
chat = sh.interfaces.Chat()
tts = sh.interfaces.TextToSpeech()
footer = sh.interfaces.Footer()

with gr.Blocks() as blocks:
    header.make_components()
    with gr.Tab('Chat'):
        chat.make_components()
    with gr.Tab('Text-To-Speech'):
        tts.make_components()
    footer.make_components()

blocks.queue().launch(
    inbrowser=False,
    share=False,
    server_name='127.0.0.1',
    server_port=8000,
    show_api=False,
)
```
