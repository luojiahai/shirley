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

- [Optional] Configure that creating the virtualenv inside the project’s root directory.
  ```
  poetry config virtualenvs.in-project true
  ```
- Create and activate the virtual environment.
  ```
  poetry shell
  ```

### Setup dependencies

- Install dependencies.
  ```
  poetry install
  ```
- Install [PyTorch](https://pytorch.org/get-started/locally/).
- Download [Qwen-VL-Chat](https://huggingface.co/Qwen/Qwen-VL-Chat) and save it locally.
- Update `config.ini` accordingly.

### Setup database

- Migrate.
  ```
  poetry run python shirley/manage.py migrate
  ```
- Create super user.
  ```
  poetry run python shirley/manage.py createsuperuser
  ```

## Usage

- Activate the virtual environment.
  ```
  poetry shell
  ```

### Commands

- Run server.
  ```
  poetry run shirley/manage.py runserver
  ```
- Run PoC.
  ```
  poetry run poc
  ```
- Run tests.
  ```
  poetry run pytest
  ```
