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
                f'Pretrained model not found in path {pretrained_model_path}.'
            )

        tokenizer = QWenTokenizer.from_pretrained(
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
                device=self.device,
            )
        if model.generation_config.eos_token_id is not None:
            model.generation_config.eos_token_id = torch.tensor(
                [model.generation_config.eos_token_id],
                device=self.device,
            )

        self._tokenizer = tokenizer
        self._model = model.to(device=self.device)

        return

    @property
    def device(self) -> torch.device:
        if torch.cuda.is_available():
            device = torch.device('cuda')
        elif torch.backends.mps.is_available():
            device = torch.device('mps')
        else:
            device = torch.device('cpu')
        return device

    @property
    def tokenizer(self) -> QWenTokenizer:
        return self._tokenizer

    @property
    def model(self) -> QWenLMHeadModel:
        return self._model

    def generate(self, text: str, history: HistoryType = None) -> Tuple[str, HistoryType]:
        query = self.tokenizer.from_list_format([{'text': text}])
        return self.model.chat(tokenizer=self.tokenizer, query=query, history=history)
