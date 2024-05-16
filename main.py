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
Human: You are a question answering Assistant. I will provide you with a user's
question, your job is to answer the user's question.

Here is the user's question:
<question>
{query}
</question>

Assistant:
'''

inputs = tokenizer(
    text=prompt,
    return_tensors='pt',
    return_attention_mask=False,
)
inputs.to(device=device)

class MyStoppingCriteria(transformers.StoppingCriteria):
    def __init__(self, target_sequence, prompt):
        self.target_sequence = target_sequence
        self.prompt=prompt

    def __call__(self, input_ids, scores, **kwargs):
        generated_text = tokenizer.decode(input_ids[0])
        generated_text = generated_text.replace(self.prompt, '')
        if self.target_sequence in generated_text:
            return True
        return False

    def __len__(self):
        return 1

    def __iter__(self):
        yield self

stop_sequence = 'User:'

outputs = model.generate(
    **inputs,
    max_length=256,
    do_sample=True,
    pad_token_id=tokenizer.eos_token_id,
    stopping_criteria=MyStoppingCriteria(stop_sequence, prompt),
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
