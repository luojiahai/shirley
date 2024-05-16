# My AI App

This application generates text using [Mistral-7B-Instruct-v0.2](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2) model.

## Requirements
- Git
- CUDA if using NVIDIA graphics cards

## Installation

### Windows
- Run `install.bat`. It does the following automatically:
    - Install [Python 3.10.6](https://www.python.org/downloads/release/python-3106/) Windows embeddable package to `python` directory.
    - Download [get-pip.py](https://bootstrap.pypa.io/get-pip.py) to `python` directory.
    - Remove `*._pth` file from `python` directory.
    - Install [pip](https://pypi.org/project/pip/) from `python/get-pip.py`.
- Run `python\Scripts\pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121`.
- Run `python\Scripts\pip3 install transformers`.
- Download [Mistral-7B-Instruct-v0.2](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2) model to `models` directory.

### MacOS
- Install [Python 3.10.6](https://www.python.org/downloads/release/python-3106/).
- Install [pip](https://pypi.org/project/pip/).
- Run `pip3 install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cpu`.
  - The Preview (Nightly) build of PyTorch will provide the latest mps support on your device. https://developer.apple.com/metal/pytorch/
- Run `pip3 install transformers`.
- Download [Mistral-7B-Instruct-v0.2](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2) model to `models` directory.

## Usage

Update `prompt` in `main.py`.

### Windows
- Run `run.bat`.

### MacOS
- Run `python3 main.py`.
