import os
import shirley.utils
import torch
import transformers
from models.qwen_vl_chat.modeling_qwen import QWenLMHeadModel
from models.qwen_vl_chat.tokenization_qwen import QWenTokenizer
from models.qwen_vl_chat.qwen_generation_utils import HistoryType
from typing import List, Tuple


class Generator(object):

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
    
    def augment(self, task_history: List[Tuple]) -> Tuple[str, HistoryType]:
        history = []
        picture_index = 1
        text = ''
        for _, (query, response) in enumerate(task_history):
            if isinstance(query, (Tuple, List)):
                file_path = query[0]
                if shirley.utils.is_image(file_path):
                    query = f'Picture {picture_index}: <img>{file_path}</img>'
                    text += query + '\n'
                    picture_index += 1
                else:
                    # TODO: other file types
                    pass
            else:
                text += query
                history.append((text, response))
                text = ''
        return history[-1][0], history[:-1]

    def generate(self, text: str, history: HistoryType = None) -> Tuple[str, HistoryType]:
        chat = [{'text': text}]
        query = self.tokenizer.from_list_format(chat)
        return self.model.chat(tokenizer=self.tokenizer, query=query, history=history)
