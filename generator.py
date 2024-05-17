import os
import torch
import transformers

class Generator(object):
    def __init__(self):
        if not os.path.exists(self.pretrained_model_path):
            error_message = f'Directory {self.pretrained_model_path} not found.'
            raise FileNotFoundError(error_message)

        if torch.cuda.is_available():
            self._device = torch.device('cuda')
        elif torch.backends.mps.is_available():
            self._device = torch.device('mps')
        else:
            self._device = torch.device('cpu')

        self._model = transformers.AutoModelForCausalLM.from_pretrained(
            pretrained_model_name_or_path=self.pretrained_model_path,
            local_files_only=True,
            torch_dtype=torch.bfloat16,
        )

        self._tokenizer = transformers.AutoTokenizer.from_pretrained(
            pretrained_model_name_or_path=self.pretrained_model_path,
            local_files_only=True,
        )

        self._pipeline = transformers.pipeline(
            task='text-generation',
            model=self.model,
            tokenizer=self.tokenizer,
            device=self.device,
        )

    @property
    def pretrained_model_path(self):
        return 'models/Mistral-7B-Instruct-v0.2'

    @property
    def device(self):
        return self._device

    @property
    def model(self):
        return self._model

    @property
    def tokenizer(self):
        return self._tokenizer

    @property
    def pipeline(self):
        return self._pipeline

    def generate(self, prompt: str) -> str:
        text_inputs = [{'role': 'user', 'content': prompt}]
        text_outputs = self.pipeline(
            text_inputs=text_inputs,
            max_new_tokens=256,
            do_sample=True,
            pad_token_id=self.tokenizer.eos_token_id,
        )
        return text_outputs[0]['generated_text']
