## 🦈 Shirley

It intelligently chats, powered by [Qwen/Qwen-VL-Chat](https://huggingface.co/Qwen/Qwen-VL-Chat) (通义千问).

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

### Setup pretrained model

Install submodule:
```
git submodule update --init --recursive
```

Update submodule:
```
git submodule update --remote --merge
```

## Usage

Activate the virtual environment:
```bash
poetry shell
```

### Running

Run WebUI:
```bash
poetry run webui
```

Run poc:
```bash
poetry run poc
```

Run tests:
```bash
poetry run pytest
```
