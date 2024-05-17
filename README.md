# Shirley 🦈

This tool generates text using [Mistral-7B-Instruct-v0.2](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2) model.

## Requirements
- [Git](https://git-scm.com/)
- [CUDA](https://developer.nvidia.com/cuda-toolkit) if using NVIDIA graphics cards
- [Python 3.10.6](https://www.python.org/downloads/release/python-3106/) and [pip](https://pypi.org/project/pip/) if on MacOS / Linux

## Installation

Python is not required for this installation on Windows.

### Windows
- Run `install.bat`, which creates Python environment locally.
- Install [PyTorch](https://pytorch.org/get-started/locally/).
  ```
  python\Scripts\pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
  ```
- Install all dependencies in `requirements.txt`.
    ```
    python\Scripts\pip3 install -r requirements.txt
    ```
- Download [Mistral-7B-Instruct-v0.2](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2) model to `models` directory.

### MacOS (Apple Silicon)
- Install [PyTorch](https://pytorch.org/get-started/locally/) Preview (Nightly).
  - The Preview (Nightly) build of PyTorch will provide the latest mps support on your device. See https://developer.apple.com/metal/pytorch/.
- Install all dependencies in `requirements.txt`.
- Download [Mistral-7B-Instruct-v0.2](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2) model to `models` directory.

### MacOS (Intel) / Linux
- Install [PyTorch](https://pytorch.org/get-started/locally/).
- Install all dependencies in `requirements.txt`.
- Download [Mistral-7B-Instruct-v0.2](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2) model to `models` directory.

## Usage

Update `prompt` in `main.py`.

### Windows
- Run `run.bat`.

### MacOS / Linux
- Run `python3 main.py`.
