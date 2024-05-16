print('Hello, World!')
print()

import torch
import transformers

print('BEGIN INITIALIZATION')

device = 'cpu'
use_cuda = torch.cuda.is_available()
use_mps = torch.backends.mps.is_available()

if use_cuda:
    device = torch.device('cuda')
    print('CUDA device name:', torch.cuda.get_device_properties('cuda').name)
    print('Flash Attention available:', torch.backends.cuda.flash_sdp_enabled())
elif use_mps:
    # https://developer.apple.com/metal/pytorch/
    device = torch.device('mps')
else:
    device = torch.device('cpu')
print(f'Using {device} device')

print('Torch version:', torch.__version__)
print('Transformers version:', transformers.__version__)

print('END INITIALIZATION')
print()

print('BEGIN GENERATION')

model_path = 'models/phi-2'

model = transformers.AutoModelForCausalLM.from_pretrained(
    pretrained_model_name_or_path=model_path,
    local_files_only=True,
    torch_dtype=torch.bfloat16,
)
model = model.to(device=device)

tokenizer = transformers.AutoTokenizer.from_pretrained(
    pretrained_model_name_or_path=model_path,
    local_files_only=True,
)

prompt = 'What is potato?'

messages = [
    {"role": "user", "content": prompt},
]

tokenized_chat = tokenizer.apply_chat_template(
    messages,
    tokenize=True,
    add_generation_prompt=True,
    return_tensors="pt"
)
tokenized_chat = tokenized_chat.to(device=device)

outputs = model.generate(
    tokenized_chat,
    max_length=256,
    do_sample=True,
    pad_token_id=tokenizer.eos_token_id,
)

text = tokenizer.batch_decode(outputs)[0]

print('END GENERATION')
print()

print('BEGIN PRINT OUTPUT')
print(text)
print('END PRINT OUTPUT')
print()
