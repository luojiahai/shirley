import os
import torch
import transformers
from models.qwen_vl_chat.modeling_qwen import QWenLMHeadModel
from models.qwen_vl_chat.tokenization_qwen import QWenTokenizer
from models.qwen_vl_chat.qwen_generation_utils import HistoryType
from typing import Tuple


class Client(object):

    def __init__(self, pretrained_model_path: str) -> None:
        if not os.path.exists(pretrained_model_path):
            raise FileNotFoundError(
                f'Model not found in path {pretrained_model_path}.'
            )

        if torch.cuda.is_available():
            self._device = torch.device('cuda')
        elif torch.backends.mps.is_available():
            self._device = torch.device('mps')
        else:
            self._device = torch.device('cpu')

        self._tokenizer = QWenTokenizer.from_pretrained(
            pretrained_model_name_or_path=pretrained_model_path,
            local_files_only=True,
        )

        model = QWenLMHeadModel.from_pretrained(
            pretrained_model_name_or_path=pretrained_model_path,
            local_files_only=True,
        )

        model.generation_config = transformers.GenerationConfig.from_pretrained(
            pretrained_model_name=pretrained_model_path,
            local_files_only=True,
            trust_remote_code=True,
        )

        if model.generation_config.pad_token_id is not None:
            model.generation_config.pad_token_id = torch.tensor(
                [model.generation_config.pad_token_id],
                device=self._device,
            )
        if model.generation_config.eos_token_id is not None:
            model.generation_config.eos_token_id = torch.tensor(
                [model.generation_config.eos_token_id],
                device=self._device,
            )

        self._model = model.to(device=self._device)

        return

    @property
    def device(self) -> torch.device:
        return self._device

    @property
    def tokenizer(self) -> QWenTokenizer:
        return self._tokenizer

    @property
    def model(self) -> QWenLMHeadModel:
        return self._model

    def generate(self, text: str, history: HistoryType = None) -> Tuple[str, HistoryType]:
        chat = [{'text': text}]
        query = self.tokenizer.from_list_format(chat)
        return self.model.chat(tokenizer=self.tokenizer, query=query, history=history)
