# Develop 🦈 Shirley

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

### [Chat] Setup Qwen-VL-Chat model (local)

Install and update the submodule:
```
git submodule update --init --recursive ./models/qwen_vl_chat
git submodule update --remote --merge ./models/qwen_vl_chat
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
