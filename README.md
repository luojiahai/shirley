## 🦈 Shirley

[![shirley](https://img.shields.io/badge/Shirley-06b6d4?style=flat-square)](.)
[![build](https://img.shields.io/github/actions/workflow/status/luojiahai/shirley/python-publish.yml?branch=main&style=flat-square&logo=githubactions&logoColor=white)](https://github.com/luojiahai/shirley/actions/workflows/python-publish.yml)
[![license](https://img.shields.io/github/license/luojiahai/shirley.svg?style=flat-square&logo=github&logoColor=white)](./LICENSE)
[![python](https://img.shields.io/pypi/pyversions/shirley?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![pypi](https://img.shields.io/pypi/v/shirley?style=flat-square&logo=pypi&logoColor=white)](https://pypi.org/project/shirley/)

It is just doing some stuff intelligently. It has the following features:
- Chat, powered by [Qwen/Qwen-VL-Chat](https://huggingface.co/Qwen/Qwen-VL-Chat) (通义千问).
- Text-To-Speech, powered by [Azure AI Speech](https://azure.microsoft.com/products/ai-services/ai-speech).

## Requirements

- [Git](https://git-scm.com/)
- [CUDA](https://developer.nvidia.com/cuda-toolkit) if using NVIDIA graphics cards
- [Python 3.10.6](https://www.python.org/downloads/release/python-3106/)
- [pip](https://pypi.org/project/pip/)
- [poetry](https://python-poetry.org/)

## Installation

### Setup virtual environment

[Optional] Configure that creating the virtualenv inside the project’s root directory:
```bash
poetry config virtualenvs.in-project true
```

If you are not using Python 3.10.6, you need to install the specific version. Alternatively, use `pyenv` to manage
Python versions:
```bash
pyenv install 3.10.6
```

Use Python 3.10.6 for the environment:
```bash
poetry env use <PATH>
```

Create and activate the virtual environment:
```bash
poetry shell
```

### Setup dependencies

Install dependencies:
```bash
poetry install
```

Install [PyTorch](https://pytorch.org/get-started/locally/).

### [Chat] Setup Qwen model

Install submodule:
```
git submodule update --init --recursive
```

Update submodule:
```
git submodule update --remote --merge
```

### [Text-To-Speech] Setup Azure AI Speech

Create [AI Speech](https://azure.microsoft.com/products/ai-services/ai-speech) service in Azure portal.

Set environment variables:
```
export SPEECH_KEY=your-key
export SPEECH_REGION=your-region
```

## Running

Activate the virtual environment:
```bash
poetry shell
```

Run WebUI:
```bash
poetry run webui
```

Run tests (not available yet):
```bash
poetry run pytest
```

## WebUI Usage

TODO

