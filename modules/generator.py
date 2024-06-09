import os
from typing import Union
import torch
from transformers.modeling_utils import PreTrainedModel
from transformers.models.auto.modeling_auto import AutoModelForCausalLM
from transformers.models.auto.tokenization_auto import AutoTokenizer
from transformers.pipelines import pipeline
from transformers.pipelines.base import Pipeline
from transformers.tokenization_utils import PreTrainedTokenizer
from transformers.tokenization_utils_fast import PreTrainedTokenizerFast

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

        self._model = AutoModelForCausalLM.from_pretrained(
            pretrained_model_name_or_path=pretrained_model_path,
            local_files_only=True,
            torch_dtype=torch.bfloat16,
        )
        self._tokenizer = AutoTokenizer.from_pretrained(
            pretrained_model_name_or_path=pretrained_model_path,
            local_files_only=True,
        )
        self._pipeline = pipeline(
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
    def model(self) -> PreTrainedModel:
        return self._model

    @property
    def tokenizer(self) -> Union[PreTrainedTokenizer, PreTrainedTokenizerFast]:
        return self._tokenizer

    @property
    def pipeline(self) -> Pipeline:
        return self._pipeline

    def generate(self, prompt: str) -> str:
        text_outputs = self.pipeline(
            text_inputs=prompt,
            return_full_text=False,
            max_new_tokens=256,
            do_sample=True,
            pad_token_id=self.tokenizer.eos_token_id,
        )
        return text_outputs[0]['generated_text']
