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
            bf16=True,
        )

        self._tokenizer = transformers.AutoTokenizer.from_pretrained(
            pretrained_model_name_or_path=pretrained_model_path,
            local_files_only=True,
            trust_remote_code=True,
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

    def generate(self, prompt: str, history=None) -> str:
        model = self.model.to(device=self.device)
        query = self.tokenizer.from_list_format([{'text': prompt}])
        response, history = model.chat(self.tokenizer, query=query, history=history)
        return response
