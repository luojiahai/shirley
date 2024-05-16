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

print('Torch version:', torch.version.__version__)
print('Transformers version:', transformers.__version__)

print('END INITIALIZATION')
print()

print('BEGIN GENERATION')

model = transformers.AutoModelForCausalLM.from_pretrained(
    pretrained_model_name_or_path='models/phi-2',
    local_files_only=True,
    torch_dtype=torch.bfloat16,
    trust_remote_code=True,
)
model.to(device=device)

tokenizer = transformers.AutoTokenizer.from_pretrained(
    pretrained_model_name_or_path='models/phi-2',
    local_files_only=True,
    trust_remote_code=True,
)

query = 'What is potato?'

prompt = f'''
User: {query}
Assistant:
'''

inputs = tokenizer(
    text=prompt,
    return_tensors='pt',
    return_attention_mask=False,
)
inputs.to(device=device)

stop_sequence = 'User:'

def custom_stopping_criteria(input_ids, scores, **kwargs):
    generated_text = tokenizer.decode(input_ids[0])
    generated_text = generated_text.replace(prompt, '')
    if stop_sequence in generated_text:
        return True
    return False

outputs = model.generate(
    **inputs,
    max_length=256,
    do_sample=True,
    pad_token_id=tokenizer.eos_token_id,
    stopping_criteria=transformers.StoppingCriteriaList([custom_stopping_criteria]),
)

text = tokenizer.batch_decode(outputs)[0]
text = text \
    .replace(prompt, '') \
    .replace(stop_sequence, '') \
    .replace('<|endoftext|>', '') \
    .strip()

print('END GENERATION')
print()

print('BEGIN PRINT OUTPUT')
print(text)
print('END PRINT OUTPUT')
print()
