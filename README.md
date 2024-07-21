## 🦈 Shirley

It intelligently chats, powered by [Qwen/Qwen-VL-Chat](https://huggingface.co/Qwen/Qwen-VL-Chat) (通义千问).

## Requirements
- [Git](https://git-scm.com/)
- [CUDA](https://developer.nvidia.com/cuda-toolkit) if using NVIDIA graphics cards
- [Python 3.10.6](https://www.python.org/downloads/release/python-3106/)
- [pip](https://pypi.org/project/pip/)

## Installation

- Setup virtual environment.
  ```
  python -m venv .venv
  ```
- Activate virtual environment.
- Install [PyTorch](https://pytorch.org/get-started/locally/).
- Install all dependencies in `requirements.txt`.
  ```
  pip install -r requirements.txt
  ```
- Download [Qwen-VL-Chat](https://huggingface.co/Qwen/Qwen-VL-Chat).
- Update `config.ini` accordingly.

## Usage

- Migrate database.
  ```
  python manage.py migrate
  ```
- Run server.
  ```
  python manage.py runserver
  ```
