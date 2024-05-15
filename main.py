print('Hello, World!')

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

torch.set_default_device("cuda")
print('Device name:', torch.cuda.get_device_properties('cuda').name)
print('Flash Attention available:', torch.backends.cuda.flash_sdp_enabled())
print('Torch version:', torch.version.__version__)

model = AutoModelForCausalLM.from_pretrained(
    pretrained_model_name_or_path="./models/phi-2",
    local_files_only=True,
    torch_dtype="auto",
    trust_remote_code=True,
)

tokenizer = AutoTokenizer.from_pretrained(
    pretrained_model_name_or_path="./models/phi-2",
    local_files_only=True,
    trust_remote_code=True,
)

prompt = '''
def print_prime(n):
   """
   Print all primes between 1 and n
   """
'''

inputs = tokenizer(
    text=prompt,
    return_tensors="pt",
    return_attention_mask=False,
)

outputs = model.generate(
    **inputs,
    max_length=200,
    pad_token_id=tokenizer.eos_token_id,
)

text = tokenizer.batch_decode(outputs)[0]

print('-- START OUTPUT ---')
print(text)
print('--- END OUTPUT ---')
