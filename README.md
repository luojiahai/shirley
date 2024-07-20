g# 🦈 Shirley

This generates text using the [Qwen/Qwen-VL-Chat](https://huggingface.co/Qwen/Qwen-VL-Chat) model with RAG support using the [sentence-transformers/all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) embeddings model.

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
- Download [Qwen-VL-Chat](https://huggingface.co/Qwen/Qwen-VL-Chat) model and save it to `models` directory.
- Download [all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) model and save it to `models` directory.

### MacOS (Apple Silicon)
- Install [PyTorch](https://pytorch.org/get-started/locally/) Preview (Nightly).
  - The Preview (Nightly) build of PyTorch will provide the latest mps support on your device. See https://developer.apple.com/metal/pytorch/.
- Install all dependencies in `requirements.txt`.
- Download [Mistral-7B-Instruct-v0.2](https://huggingface.co/Qwen/Qwen-VL-Chat) model to `models` directory.
- Download [all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) model to `models` directory.

### MacOS (Intel) / Linux
- Install [PyTorch](https://pytorch.org/get-started/locally/).
- Install all dependencies in `requirements.txt`.
- Download [Qwen-VL-Chat](https://huggingface.co/Qwen/Qwen-VL-Chat) model and save it to `models` directory.
- Download [all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) model and save it to `models` directory.

## Usage

- Update `config.ini` to specify the configuration.
- Write prompt in `prompt.txt`.

### Windows
- Run `run.bat`.

### MacOS / Linux
- Run `python3 main.py`.
