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

## Download models

- Download [Qwen-VL-Chat](https://huggingface.co/Qwen/Qwen-VL-Chat).
- Download [all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2).

## Usage

- Update `config.ini` to specify the configuration accordingly.
- Write prompt in `prompt.txt`.
