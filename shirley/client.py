import logging
import os
import pathlib
import shirley as sh
import sys
import torch
import transformers
import uuid
from models.qwen_vl_chat.modeling_qwen import QWenLMHeadModel
from models.qwen_vl_chat.tokenization_qwen import QWenTokenizer
from typing import Any, Generator, Tuple


logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


class Client(object):

    def __init__(self, pretrained_model_name_or_path: str) -> None:
        if not os.path.exists(pretrained_model_name_or_path):
            raise FileNotFoundError(f'Pretrained model not found in path {pretrained_model_name_or_path}.')

        if torch.cuda.is_available():
            self._device = torch.device('cuda')
            print(f'CUDA device: {torch.cuda.get_device_name(torch.cuda.current_device())}')
        elif torch.backends.mps.is_available():
            self._device = torch.device('mps')
        else:
            self._device = torch.device('cpu')

        tokenizer = QWenTokenizer.from_pretrained(
            pretrained_model_name_or_path=pretrained_model_name_or_path,
            local_files_only=True,
        )

        model = QWenLMHeadModel.from_pretrained(
            pretrained_model_name_or_path=pretrained_model_name_or_path,
            local_files_only=True,
        )

        model.generation_config = transformers.GenerationConfig.from_pretrained(
            pretrained_model_name=pretrained_model_name_or_path,
            local_files_only=True,
            trust_remote_code=True,
        )

        if model.generation_config.pad_token_id is not None:
            model.generation_config.pad_token_id = torch.tensor(
                data=[model.generation_config.pad_token_id],
                device=self.device,
            )
        if model.generation_config.eos_token_id is not None:
            model.generation_config.eos_token_id = torch.tensor(
                data=[model.generation_config.eos_token_id],
                device=self.device,
            )

        self._tokenizer = tokenizer
        self._model = model.to(device=self.device)


    @property
    def device(self) -> torch.device:
        return self._device

    @property
    def tokenizer(self) -> QWenTokenizer:
        return self._tokenizer

    @property
    def model(self) -> QWenLMHeadModel:
        return self._model


    def chat(self, query: str, history: sh.ChatHistory = None) -> Tuple[str, sh.ChatHistory]:
        return self.model.chat(tokenizer=self.tokenizer, query=query, history=history)


    def chat_stream(self, query: str, history: sh.ChatHistory = None) -> Generator[str, Any, None]:
        return self.model.chat_stream(tokenizer=self.tokenizer, query=query, history=history)


    def draw_bbox_on_latest_picture(self, history: sh.ChatHistory, tempdir: str) -> str | None:
        response = history[-1][1]
        image = self.tokenizer.draw_bbox_on_latest_picture(response=response, history=history)
        if image is not None:
            images_tempdir = pathlib.Path(tempdir) / 'images'
            images_tempdir.mkdir(exist_ok=True, parents=True)
            name = f'img-{uuid.uuid4()}.jpg'
            filename = images_tempdir / name
            image.save(str(filename))
            return str(filename)
        return None
