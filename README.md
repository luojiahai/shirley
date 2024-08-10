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

## Quick tour

```python
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

## Development

See [DEVELOPMENT.md](./DEVELOPMENT.md).
