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

Download [Qwen-VL-Chat](https://huggingface.co/Qwen/Qwen-VL-Chat) and save it locally (in any location).

### Setup Django

Create a file `secret_key.txt` in root directory.

Generate a random string and put it into the file:
```python
>>> from django.core.management.utils import get_random_secret_key
>>> get_random_secret_key()
```

Migrate database:
```bash
poetry run python shirley/manage.py migrate
```

Create super user:
```bash
poetry run python shirley/manage.py createsuperuser
```

### Configuration

Update configuration `config.ini` if necessary.

## Usage

Activate the virtual environment:
```bash
poetry shell
```

### Running

Run server:
```bash
poetry run shirley/manage.py runserver
```

Run poc:
```bash
poetry run poc
```

Run tests:
```bash
poetry run pytest
```
