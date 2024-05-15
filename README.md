# My AI App

## Installation

### Installation on Windows using embeddable package
- Run `install_windows.bat`.
- Use `python/Scripts/pip3` to install the following dependencies.
    - PyTorch: `install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121`.
    - Transformers: `install transformers`.

### Installation on Windows using embeddable package (manually)
- Download Python Windows embeddable package and extract in `python`.
- Uncomment `#import site` in `python/<python_version>._pth`.
- Download `get-pip.py` from https://bootstrap.pypa.io/get-pip.py and place here.
- Run `python/python.exe get-pip.py`.
- Use `python/Scripts/pip3` to install the following dependencies.
    - PyTorch: `install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121`.
    - Transformers: `install transformers`.
- Download Git Windows portable and extract in `git`.

### Installation on Windows
1. Install [Python 3.10.6](https://www.python.org/downloads/release/python-3106/) (Newer version of Python does not support torch), checking "Add Python to PATH".
2. Install [git](https://git-scm.com/download/win).
3. Clone this repository.
4. Run `install_windows.bat`.

## Models
- Explore https://huggingface.co/ for models.
- Clone the repository in `models/<model_repository>` via `git`.
    - Alternatively, download the repository zip and extract in `models/<model_repository>`.

## Usage
- Update `main.py` for the model path.
- Update `prompt` if needed.
- Run `run.bat`.
