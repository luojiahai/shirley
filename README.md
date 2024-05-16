# My AI App

## Installation
- Run `install.bat`. It does automatically:
    - Install [Python 3.10.6](https://www.python.org/downloads/release/python-3106/) Windows embeddable package to `python` directory.
    - Download [get-pip.py](https://bootstrap.pypa.io/get-pip.py) to `python` directory.
    - Remove `*._pth` file from `python` directory.
    - Install [pip](https://pypi.org/project/pip/) from `python/get-pip.py`.
- Run `python\Scripts\pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121`
- Run `python\Scripts\pip3 install transformers`

## Usage
- Explore models on https://huggingface.co/.
- Choose your favourite one.
- Install the model to `models` directory.
- Overwrite `main.py` with your code to use the chosen model.
- Run `run.bat`.

### Example: microsoft/phi-2
- Run `git lfs install`.
- Run `git clone https://huggingface.co/microsoft/phi-2 models`.
- Overwrite `main.py` with the sample code below.
    ```
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    torch.set_default_device("cuda")

    model = AutoModelForCausalLM.from_pretrained("microsoft/phi-2", torch_dtype="auto", trust_remote_code=True)
    tokenizer = AutoTokenizer.from_pretrained("microsoft/phi-2", trust_remote_code=True)

    inputs = tokenizer('''def print_prime(n):
    """
    Print all primes between 1 and n
    """''', return_tensors="pt", return_attention_mask=False)

    outputs = model.generate(**inputs, max_length=200)
    text = tokenizer.batch_decode(outputs)[0]
    print(text)
    ```
- Run `run.bat`.
