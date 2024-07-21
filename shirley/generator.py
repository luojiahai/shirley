import os
import torch
import transformers
from typing import Union


class Generator(object):
    def __init__(self, pretrained_model_path: str) -> None:
        if not os.path.exists(pretrained_model_path):
            raise FileNotFoundError(
                f'Model path {pretrained_model_path} not found.'
            )

        if torch.cuda.is_available():
            self._device = torch.device('cuda')
        elif torch.backends.mps.is_available():
            self._device = torch.device('mps')
        else:
            self._device = torch.device('cpu')

        self._model = transformers.AutoModelForCausalLM.from_pretrained(
            pretrained_model_name_or_path=pretrained_model_path,
            local_files_only=True,
            trust_remote_code=True,
            torch_dtype=torch.bfloat16,
        )
        self._tokenizer = transformers.AutoTokenizer.from_pretrained(
            pretrained_model_name_or_path=pretrained_model_path,
            local_files_only=True,
            trust_remote_code=True,
        )
        self._pipeline = transformers.pipeline(
            task='text-generation',
            model=self.model,
            tokenizer=self.tokenizer,
            device=self.device,
        )
        return

    @property
    def device(self) -> torch.device:
        return self._device

    @property
    def model(self) -> transformers.PreTrainedModel:
        return self._model

    @property
    def tokenizer(self) -> Union[transformers.PreTrainedTokenizer, transformers.PreTrainedTokenizerFast]:
        return self._tokenizer

    @property
    def pipeline(self) -> transformers.Pipeline:
        return self._pipeline

    def generate(self, prompt: str) -> str:
        text_outputs = self.pipeline(
            text_inputs=prompt,
            return_full_text=False,
            pad_token_id=self.tokenizer.eos_token_id,
        )
        return text_outputs[0]['generated_text']
