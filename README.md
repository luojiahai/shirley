# My AI App

## Initialization
- Download Python Windows embeddable package and extract in `.\python`
- Uncomment `#import site` in `.\python\<python_version>._pth`
- Download `get-pip.py` from https://bootstrap.pypa.io/get-pip.py and place here
- Run `.\python\python.exe get-pip.py`
- Use `.\python\Scripts\pip3` to install the following dependencies
    - PyTorch: `install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121`
    - Transformers: `install transformers`
- Download Git Windows portable and extract in `.\git`

## Install Models
- Explore https://huggingface.co/ for models
- Clone the repository in `.\models\<model_repository>`, alternatively download the zip and extract in `.\`
