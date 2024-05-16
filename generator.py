import os
from typing import Dict, List, TypeAlias, Union
import torch
import transformers

Model: TypeAlias = transformers.PreTrainedModel
Tokenizer: TypeAlias = Union[transformers.PreTrainedTokenizer, transformers.PreTrainedTokenizerFast]
Input: TypeAlias = Union[str, List[str], List[Dict[str, str]], List[List[Dict[str, str]]]]
Output: TypeAlias = Union[List[Dict[str, str]], List[Dict[str, List[Dict[str, str]]]]]

class Generator(object):
    models_directory: os.PathLike[str] = 'models'
    model_name: str = 'Mistral-7B-Instruct-v0.2'
    model_path: os.PathLike[str] = f'{models_directory}/{model_name}'
    model_torch_dtype: torch.dtype = torch.bfloat16

    def __init__(self):
        self._device = self._create_device()
        self._model = self._create_model()
        self._tokenizer = self._create_tokenizer()
        self.pipeline = transformers.pipeline(
            task='text-generation',
            model=self.model,
            tokenizer=self.tokenizer,
            device=self.device,
        )

    @property
    def device(self) -> torch.device:
        return self._device
    
    @property
    def model(self) -> Model:
        return self._model
    
    @property
    def tokenizer(self) -> Tokenizer:
        return self._tokenizer

    def _create_device(self) -> torch.device:
        device = 'cpu'
        if torch.cuda.is_available():
            device = torch.device('cuda')
        elif torch.backends.mps.is_available():
            device = torch.device('mps')
        else:
            device = torch.device('cpu')
        return device

    def _create_model(self) -> Model:
        return transformers.AutoModelForCausalLM.from_pretrained(
            pretrained_model_name_or_path=Generator.model_path,
            local_files_only=True,
            torch_dtype=Generator.model_torch_dtype,
        )

    def _create_tokenizer(self) -> Tokenizer:
        return transformers.AutoTokenizer.from_pretrained(
            pretrained_model_name_or_path=Generator.model_path,
            local_files_only=True,
        )

    def generate(self, prompt: str) -> str:
        text_inputs: Input = [{'role': 'user', 'content': prompt}]
        text_outputs: Output = self.pipeline(
            text_inputs=text_inputs,
            return_full_text=False,
            do_sample=True,
            pad_token_id=self.tokenizer.eos_token_id,
            max_new_tokens=256,
        )
        return text_outputs[0]['generated_text'].strip()
