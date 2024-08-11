# 🦈 Shirley

[![shirley](https://img.shields.io/badge/🦈-Shirley-06b6d4?style=flat-square)](.)
[![build](https://img.shields.io/github/actions/workflow/status/luojiahai/shirley/python-publish.yml?branch=main&style=flat-square&logo=githubactions&logoColor=white)](https://github.com/luojiahai/shirley/actions/workflows/python-publish.yml)
[![license](https://img.shields.io/github/license/luojiahai/shirley.svg?style=flat-square&logo=github&logoColor=white)](./LICENSE)
[![python](https://img.shields.io/pypi/pyversions/shirley?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![pypi](https://img.shields.io/pypi/v/shirley?style=flat-square&logo=pypi&logoColor=white)](https://pypi.org/project/shirley/)

It is just doing some stuff intelligently. It has the following features:
- Chat, powered by [Qwen/Qwen-VL-Chat](https://huggingface.co/Qwen/Qwen-VL-Chat) (通义千问).
- Text-To-Speech, powered by [Azure AI Speech](https://azure.microsoft.com/products/ai-services/ai-speech).

## Installation

```bash
pip install shirley
```

### [Chat] Download `Qwen-VL-Chat` model

Add `Qwen/Qwen-VL-Chat` as a `git` submodule:
```
git submodule add https://huggingface.co/Qwen/Qwen-VL-Chat.git models/qwen_vl_chat
git submodule update --init --recursive models/qwen_vl_chat
git submodule update --remote --merge models/qwen_vl_chat
```

### [Text-To-Speech] Setup Azure AI Speech

Create [AI Speech](https://azure.microsoft.com/products/ai-services/ai-speech) service in Azure portal.

Set environment variables:
```
export SPEECH_KEY=your-key
export SPEECH_REGION=your-region
```

Set environment variables on Windows:
```
setx SPEECH_KEY your-key
setx SPEECH_REGION your-region
```

## Quicktour

```python
# webui.py

import gradio as gr
import shirley as sh

with gr.Blocks() as blocks:
    sh.interfaces.Header()
    with gr.Tab('Chat'):
        sh.interfaces.Chat()
    with gr.Tab('Text-To-Speech'):
        sh.interfaces.TextToSpeech()
    sh.interfaces.Footer()

blocks.queue().launch()
```

Note: I made a working [example](https://github.com/luojiahai/shirley/blob/main/webui.py). You can use that.

### Running

```bash
pip install -r requirements.txt
python webui.py
```

Note: I recommend using [`poetry`](https://python-poetry.org/) to manage dependencies and run Python. See [DEVELOPMENT.md](./DEVELOPMENT.md) for more details.

## Development

See [DEVELOPMENT.md](./DEVELOPMENT.md).
